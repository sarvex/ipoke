from experiments.experiment import Experiment
from functools import partial

from models.first_stage_motion_model import SpadeCondMotionModel, FCBaseline
from models.poke_vae import PokeVAE
from data.datamodule import StaticDataModule


class FirstStageSequenceModel(Experiment):

    def __init__(self,config,dirs,devices):
        super().__init__(config,dirs,devices)

        # intiliaze models
        self.datakeys = ["images"]
        self.is_baseline = 'baseline' in self.config['architecture'] and self.config['architecture']['baseline']
        self.fc_baseline = 'fc_baseline' in self.config['architecture'] and self.config['architecture']['fc_baseline']
        if self.is_baseline:
            self.datakeys.extend(['poke','flow','sample_ids'])

        model = PokeVAE if self.is_baseline else SpadeCondMotionModel
        if self.fc_baseline:
            model = FCBaseline

        if self.config["general"]["restart"] or self.config['general']['test'] != 'none':
            ckpt_path = self._get_checkpoint()
            self.ae = model.load_from_checkpoint(ckpt_path,map_location="cpu", strict=False,config=self.config,dirs= self.dirs)
        else:
            self.ae = model(self.config,dirs=self.dirs)
        # basic trainer is initialized in parent class
        # self.logger.info(
        #     f"Number of trainable parameters in model is {sum(p.numel() for p in self.ae.parameters())}"
        # )

        self.ckpt_callback = self.ckpt_callback(filename='{epoch}-{FVD-val:.3f}',monitor='FVD-val',
                                                save_top_k=self.config["logging"]["n_saved_ckpt"], mode='min')
        to_yaml_cb = self.add_ckpt_file()

        callbacks = [self.ckpt_callback,to_yaml_cb]
        if self.config["general"]["restart"] and ckpt_path is not None:
            self.basic_trainer = partial(self.basic_trainer,resume_from_checkpoint=ckpt_path,callbacks=callbacks)
        else:
            self.basic_trainer = partial(self.basic_trainer,callbacks=callbacks)

        self.basic_trainer = partial(self.basic_trainer,automatic_optimization=False,terminate_on_nan=True)

    def train(self):
        # prepare data
        datamod = StaticDataModule(self.config["data"], datakeys=self.datakeys)
        datamod.setup()
        n_batches_complete_train = len(datamod.train_dataloader())
        n_batches_complete_val = len(datamod.val_dataloader())
        n_train_batches = min(
            n_batches_complete_train,
            self.config["training"]["max_batches_per_epoch"],
        )
        n_val_batches = min(
            n_batches_complete_val, self.config["training"]["max_val_batches"]
        )

        if not self.is_debug:
            trainer = self.basic_trainer(limit_val_batches=n_val_batches,limit_train_batches=n_train_batches,
                                         limit_test_batches=n_val_batches, replace_sampler_ddp=datamod.dset_train.obj_weighting or datamod.zero_poke)
        else:
            trainer = self.basic_trainer()

        trainer.fit(self.ae, datamodule=datamod)


    def test(self):
        import math
        import torch
        from tqdm import tqdm
        from copy import deepcopy
        from utils.logging import make_errorbar_plot
        import pandas as pd
        import os

        assert self.is_baseline or self.fc_baseline

        # test without zero poke
        self.config['data']['zero_poke'] = False
        self.config['data']['test_batch_size'] = self.config['testing']['test_batch_size']
        if self.config['general']['test']=='motion_transfer':
            assert self.config['data']['dataset'] == 'IperDataset'
            self.config['data']['get_kp_nn'] = True
        if self.config['general']['test'] == 'diversity':
            n_test_batches = int(
                math.ceil(self.config['testing']['n_samples_metrics'] / self.config['data']['test_batch_size']))
            # max_n_pokes = deepcopy(self.config['data']['n_pokes'])

            # if self.config['testing']['summarize_n_pokes']:
            self.ae.console_logger.info('***************************COMPUTING METRICS OVER SUMMARIZED POKES*******************************************************')
            datamod = StaticDataModule(self.config["data"], datakeys=self.datakeys, debug=self.config['testing']['debug'])
            datamod.setup()
            trainer = self.basic_trainer(limit_test_batches=n_test_batches)
            trainer.test(self.ae, datamodule=datamod)
            # else:
            #     self.ae.console_logger.info('***************************COMPUTING METRICS FOR EACH INDIVIDUAL NUMBER OF POKES******************************************')
            #     self.config['data']['fix_n_pokes'] = True
            #     for count,n_pokes in enumerate(tqdm(reversed(range(max_n_pokes)),desc='Conducting metrics experiment....')):
            #         self.config['data']['n_pokes'] = n_pokes +1
            #         self.ae.console_logger.info(f'Instantiating {n_pokes + 1} pokes...')
            #
            #         datamod = StaticDataModule(self.config["data"], datakeys=self.datakeys, debug=self.config['testing']['debug'])
            #         datamod.setup()
            #         trainer = self.basic_trainer(limit_test_batches=n_test_batches)
            #         trainer.test(self.ae,datamodule=datamod)
            #
            # if self.config['general']['test'] == 'metrics':
            #
            #     kps_dict =self.ae.metrics_dict['KPS']
            #     ssim_dict = self.ae.metrics_dict['SSIM']
            #     lpips_dict = self.ae.metrics_dict['LPIPS']
            #     # construcr dataframes
            #     df_ssim = pd.DataFrame.from_dict(ssim_dict)
            #     # df_psnr = pd.DataFrame.from_dict(psnr_dict)
            #     df_lpips = pd.DataFrame.from_dict(lpips_dict)
            #     n_samples_per_poke = self.config['testing']['n_samples_per_data_point']
            #
            #     # save data and plot stats
            #     postfix = 'aggregated' if self.config['testing']['summarize_n_pokes'] else 'unique_pokes'
            #     # metrics only reported when gt keypoints are available
            #     if len(kps_dict) > 0:
            #         df_kps = pd.DataFrame.from_dict(kps_dict)
            #         fig_savename = os.path.join(self.ae.metrics_dir, f'keypoint_err_plot_{n_samples_per_poke}samples-{postfix}.pdf')
            #         df_kps.to_csv(os.path.join(self.ae.metrics_dir,f'plot_data_{n_samples_per_poke}pokes_kps-{postfix}.csv'))
            #         make_errorbar_plot(fig_savename,df_kps,xid='Time',yid='Mean MSE per Frame',
            #                            hueid='Number of Pokes',varid='Std per Frame')
            #         df_kps_group = df_kps.groupby('Time', as_index=False).mean()
            #         df_kps_group.to_csv(os.path.join(self.ae.metrics_dir, f'plot_data_kps_group.csv'))
            #
            #     # image based metrics which can be reported for all datasets
            #     fig_savename = os.path.join(self.ae.metrics_dir, f'ssim_plot_{n_samples_per_poke}samples-{postfix}.pdf')
            #     df_ssim.to_csv(os.path.join(self.ae.metrics_dir, f'plot_data_{n_samples_per_poke}pokes_ssim-{postfix}.csv'))
            #     make_errorbar_plot(fig_savename, df_ssim, xid='Time', yid='Mean SSIM per Frame',
            #                        hueid='Number of Pokes',varid='Std per Frame')
            #
            #     fig_savename = os.path.join(self.ae.metrics_dir, f'lpips_plot_{n_samples_per_poke}samples-{postfix}.pdf')
            #     df_lpips.to_csv(os.path.join(self.ae.metrics_dir, f'plot_data_{n_samples_per_poke}pokes_lpips-{postfix}.csv'))
            #     make_errorbar_plot(fig_savename, df_lpips, xid='Time', yid='Mean LPIPS per Frame',
            #                        hueid='Number of Pokes', varid='Std per Frame')
            #
            #     # fig_savename = os.path.join(self.ae.metrics_dir, f'psnr_plot_{n_samples_per_poke}samples.pdf')
            #     # df_psnr.to_csv(os.path.join(self.ae.metrics_dir, f'plot_data_{n_samples_per_poke}pokes_psnr.csv'))
            #     # make_errorbar_plot(fig_savename, df_psnr, xid='Time', yid='Mean PSNR per Frame',
            #     #                    hueid='Number of Pokes', varid='Std per Frame')
            #     #aggregate for all pokes
            #
            #     df_ssim_group = df_ssim.groupby('Time', as_index=False).mean()
            #     df_ssim_group.to_csv(os.path.join(self.ae.metrics_dir, f'plot_data_ssim_group.csv'))
            #     self.ae.console_logger.info(f'Mean ssim value from sample metric is {df_ssim_group["Mean SSIM per Frame"]}')
            #     # df_psnr_group=df_psnr.groupby('Number of Pokes', as_index=False).mean()
            #     # df_psnr_group.to_csv(os.path.join(self.ae.metrics_dir, f'plot_data_psnr_group.csv'))
            #     df_lpips_group = df_lpips.groupby('Time', as_index=False).mean()
            #     df_lpips_group.to_csv(os.path.join(self.ae.metrics_dir, f'plot_data_lpips_group.csv'))
            #     self.ae.console_logger.info(f'Mean lpips value from sample metric is {df_lpips_group["Mean LPIPS per Frame"]}')
            # else:
            mean_divscore = torch.mean(torch.tensor(self.ae.div_scores))
            self.ae.console_logger.info(f'Diversity score averaged over all pokes is {mean_divscore}')

        else:

            datamod = StaticDataModule(self.config["data"], datakeys=self.datakeys)
            datamod.setup()
            if self.config['general']['test'] == 'fvd':
                self.config['data']['test_batch_size'] = 16
                n_test_batches = int(math.ceil(self.config['testing']['n_samples_fvd'] / self.config['data']['test_batch_size']))
            elif self.config['general']['test'] == 'samples':
                n_test_batches = self.config['testing']['n_samples_vis'] // self.config['data']['test_batch_size']
            else:
                n_test_batches = int(math.ceil(self.config['testing']['n_samples_metrics'] / self.config['data']['test_batch_size']))



            trainer = self.basic_trainer(limit_test_batches=n_test_batches)

            trainer.test(self.ae, datamodule=datamod)