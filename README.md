# iPOKE: Poking a Still Image for Controlled Stochastic Video Synthesis
<p align="center">
  <img src="images/gui_demo2.gif" alt="Show me that GUI" />
</p>
 
[**iPOKE: Poking a Still Image for Controlled Stochastic Video Synthesis**](https://compvis.github.io/ipoke/)

[Andreas Blattmann](https://www.linkedin.com/in/andreas-blattmann-479038186/?originalSubdomain=de),
[Timo Milbich](https://timomilbich.github.io/),
[Michael Dorkenwald](https://mdork.github.io/),
[Björn Ommer](https://hci.iwr.uni-heidelberg.de/Staff/bommer)<br/>


**TL;DR** We present <em>iPOKE</em>, a model for locally controlled, stochastic video synthesis based on poking a single pixel in a static scene, that enables users to animate still images only with simple mouse drags.
<p align="center">
<img src="images/fpp_final.png" title="Overview over our model."> 
</p>

## [**Arxiv**](https://arxiv.org/pdf/2107.02790.pdf) | [**Project page**](https://compvis.github.io/ipoke/) | [**BibTeX**](#bibtex)

## Table of contents ##
1. [News](#news)
2. [Requirements](#requirements)
3. [Pretrained models](#pretrained-models)
4. [Graphical User Interface](#graphical-user-interface)
5. [Generating samples](#generating-samples)
6. [Data preparation](#data-preparation)
7. [Evaluation](#evaluation)
8. [Train your own models](#train-your-own-models)
9. [Shout-outs](#shout-outs)
10. [BibTeX](#bibtex)

## News

* We added a [quickstart colab GUI-demo](https://colab.research.google.com/drive/1sec1I_80SpG6ielaSE0n_AcI3cEKzk0l?usp=sharing) based on [`ngrok`](https://ngrok.com/) and [`streamlit`](https://streamlit.io/) for users without own hardware.


## Requirements 
A suitable conda environment named ``ipoke`` can be created with

````shell script
conda env create -f ipoke.yml 
conda activate ipoke
````

## Pretrained models 

To you can find all pretrained models [here](https://hci.iwr.uni-heidelberg.de/compvis_files/ipoke.zip). Download and extract the `zip`-file in a `<LOGDIR>` and create a symbolic link to the created repository which is named `ipoke` via
```shell script
ln -s <LOGDIR>/ipoke logs
``` 

 Here's a list of all available pretrained models, which are contained in the extracted directories. 
 
| Dataset  | Spatial Video resolution | Model Name |  FVD 
|----------|----------|----------|--------- |
| Poking Plants | 128 x 128 | plants_128 | 63.06 |
| Poking Plants | 64 x 64 | plants_64 | 56.59 |
| iPER | 128 x 128 | iper_128 | 74.53 |
| iPER | 64 x 64 | iper_64 | 81.49 |
| Human3.6m | 128 x 128 | h36m_128 | 119.77 |
| Human3.6m | 64 x 64 | h36m_64 | 111.55 |
| TaiChi-HD | 128 x 128 | taichi_128 | 100.69 |
| TaiChi-HD | 64 x 64 | taichi_64 | 96.09 |

Make sure to first [prepare the data](#data-preparation) before using our pretrained models.

## Graphical User Interface


<p align="center">
  <img src="images/gui_demo1.gif" alt="Show me that GUI" />
</p>


To get in touch with our models, use our GUI via the command

```shell script
python -m testing.gui --model_name <MODEL_NAME> --gpu <GPU_ID>
```


, where the `<MODEL_NAME>` parameter shoud be one of the model names in the above table which shows our provided pretrained models.

## Generating samples

### Controlled stochastic video synthesis

<p align="center">
  <img src="images/overview.gif" alt="Show me the samples!" />
</p>

Samples can also be automatically generated by using simulated pokes based on optical flow via
 
```shell script
python -W ignore  main.py --config config/second_stage.yaml --gpus <GPU_IDs> --model_name <MODEL_NAME> --test samples
```

The resulting videos will be saved to `<LOGDIR>/ipoke/second_stage/generated/<MODEL_NAME>/samples_best_fvd`.

### Kinematics transfer

<p align="center">
  <img src="images/kinematics_transfer.gif" alt="Show me some transfer" />
</p>
 
Moreover, our iPOKE model provides means to transfer kinematics between videos of persons with similar start pose as shown in the above examples. Similar results can be generated with
 
 ```shell script
python -W ignore  main.py --config config/second_stage.yaml --gpus <GPU_IDs> --model_name <MODEL_NAME> --test transfer
```
The resulting videos will be saved to `<LOGDIR>/ipoke/second_stage/generated/<MODEL_NAME>/transfer`.
**NOTE** This is currently only possible for the iPER dataset.

### Control sensitivity

<p align="center">
  <img src="images/control_sensitivity.gif" alt="Show me some transfer" />
</p>
 
To observe the results from different pokes at the same pixel, you can run 
 
 ```shell script
python -W ignore  main.py --config config/second_stage.yaml --gpus <GPU_IDs> --model_name <MODEL_NAME> --test control_sensititvity
```
The resulting videos will be saved to `<LOGDIR>/ipoke/second_stage/generated/<MODEL_NAME>/poke_dir_samples_best_fvd`.
**NOTE** This is currently only possible for the iPER dataset.

## Data Preparation

### Get FlowNet2 and PoseHRNet for data processing ###

As preparing the data to evaluate our pretrained models or train new ones requires to estimate optical flow maps and human poses (currently only supported for iPER), we added the respective models [Flownet2](https://github.com/NVIDIA/flownet2-pytorch) and [PoseHRNet](https://github.com/ablattmann/pose_estimation_hrnet) as a git submodules. To clone, simply run

```shell script
git submodule init
git submodule sync
git submodule update
``` 

Since Flownet2 requires cuda-10.0 and is therefore not compatible with our main conda environment, we provide a separate conda enviroment for optical flow estimation which can bet created via

```shell script
conda env create -f data_proc.yml
```
You can activate the environment and specify the right cuda version by using 

```shell script
source activate_data_proc
``` 
from the root of this repository. IMPORTANT: You have to ensure that lines 3 and 4 in the `activate_data_proc`-script add your respective ``cuda-10.0`` installation direcories to the ``PATH`` and ``LD_LIBRARY_PATH`` environment variables. This environment, however, is only required for generating the datasets and will not be required afterwards. 
Finally, you have to build the custom layers of FlowNet2 and PoseHRNet with

```shell script
cd models/flownet2
bash install.sh -ccbin <PATH TO_GCC7>
cd ../pose_estimator/lib
make
```
, where ``<PATH TO_GCC7>`` is the path to your ``gcc-7``-binary, which is usually ``/usr/bin/gcc-7`` on a linux server. Make sure that your ``data_proc`` environment is activated and that the env-variables contain the ``cuda-10.0`` installation when running the script (which is both done by running `source activate_data_proc`).
   

### Poking Plants ###

Download Poking Plants dataset from [here](https://heibox.uni-heidelberg.de/d/71de55de923646509bc4/) and extract it to a ``<TARGETDIR>``, which then contains the raw video files. 
To extract the multi-zip file, use 

```shell script
zip -s 0 poking_plants.zip --out poking_plants_unsplit.zip
unzip poking_plants_unsplit.zip
```

To extract the individual frames and estimate optical flow set the value of the field 
``raw_dir`` in ``config/data_preparation/plants.yaml`` to be ``<TARGETDIR>``, define the target location for the extracted frames (, where all frames of each video will be within a unique directory) via the field ``processed_dir`` and run

````shell script
source activate_data_proc
python -m data.prepare_dataset --config config/data_preparation/plants.yaml
````
By defining the number of parallel runs of flownet2, which will be distributed among the gpus with the ids specified in ``target_gpus``, with the ``num_workers``-argument, you can significantly speed up the optical flow estimation.  
### iPER ###

Download the zipped videos in ```iPER_1024_video_release.zip``` from [this website](https://onedrive.live.com/?authkey=%21AJL%5FNAQMkdXGPlA&id=3705E349C336415F%2188052&cid=3705E349C336415F) 
website (note that you have to create a microsoft account to get access) and extract the archive to a ```<TARGETDIR>``` similar to the above example. There, you'll also find the ``train.txt`` and ``val.txt``. Download these files and save them in the ``<TARGETDIR>`` 
Again, set the undefined value of the field ``raw_dir`` in ``config/data_preparation/iper.yaml`` to be ``<TARGETDIR>``, define the target location for the extracted frames and the optical flow via ``processed_dir`` and run 
```shell script
python -m data.prepare_dataset --config config/data_preparation/iper.yaml
``` 
with the ````flownet2```` environment activated. 

### Human3.6m ###

Firstly, you will need to create an account at [the homepage of the Human3.6m dataset](http://vision.imar.ro/human3.6m/) to gain access to the dataset. After your account is created and approved (takes a couple of hours), log in and inspect your cookies to find your `PHPSESSID`. 
Fill in that `PHPSESSID` in `data/config.ini` and also specify the `TARGETDIR` there, where the extracted videos will be later stored. After setting the field `processed_dir` in `config/data_preparation/human36m.yaml`, you can download and extract the videos via
```shell script
source activate_data_proc
python -m data.human36m_preprocess
```
with the ````flownet2```` environment activated. 
Frame extraction and optical flow estimation are then done as usual with
```shell script
source activate_data_proc
python -m data.prepare_dataset --config config/data_preparation/human36m.yaml
```

### TaiChi-HD ###

To download and extract the videos, follow the steps listed at the [download page](https://github.com/AliaksandrSiarohin/first-order-model/tree/master/data/taichi-loading) for this dataset and set the `out_folder` argument of the script `load_videos.py` to be our `<TARGETDIR>` from the above examples. Again set the fields `raw_dir` and `processed_dir` in `config/data_preparation/taichi.yaml` similar to the above examples and run
```shell script
source activate_data_proc
python -m data.prepare_dataset --config config/data_preparation/taichi.yaml
```
with the `flownet2` environment activated to extract the individual frames and estimate the optical flow maps.


## Evaluation

To reproduce the quantitative results presented in the paper for all our provided pretrained models, run 

```shell script
python -m testing.eval_models --gpu <GPU_ID> -e <TEST_MODE>
```

where `TEST_MODE` should be in `[fvd, accuracy, diversity, kps_acc]`. The models which shall be evaluated are specified in the file `config/model_names.txt`. Here's an explanation of the different values of the `<TEST_MODE>` parameter:

| <TEST_MODE>  | Experiment | Comment | 
|----------|----------|----------|
| `fvd` | Compute FVD scores | if you encounter `tensorflow` errors due to missing libraries add `LD_LIBRARY_PATH=/usr/local/<LOCAL_CUDA_VERSION>/targets/x86_64-linux/lib/` before the above command. (Tested under Ubuntu 20.04 LTS)| 
| `accuracy` | Calculate accuracy scores `[LPIPS, SSIM, PSNR]` | as explained in the [paper](https://arxiv.org/pdf/2107.02790.pdf), results are printed to console and are also saved to `logs/second_stage/generated/<MODEL_NAME>/metrics/` for the respective model| 
| `diversity` | Calculate diversity scores based on `[LPIPS, MSE]` | as explained in the [paper](https://arxiv.org/pdf/2107.02790.pdf) , results are printed to console and are also saved to `logs/second_stage/generated/<MODEL_NAME>/metrics/` for the respective model | 
| `kps_acc` | Targeted keypoint accuracy only for the poked body parts | For a detailed explanation, see Fig. 8 and the respective section in the [paper](https://arxiv.org/pdf/2107.02790.pdf); Only supported for the models trained on the iPER dataset.  | 

If you only want to calculate the metrics only for one of our models or if you want to test [your own one](#train-your-own-models), run 

```shell script
python -W ignore main.py --config config/second_stage.yaml --model_name <MODEL_NAME> --gpus <GPU_IDs> --test <TEST_MODE>
``` 

Again, make sure to add `LD_LIBRARY_PATH=/usr/local/<LOCAL_CUDA_VERSION>/targets/x86_64-linux/lib/` before the command if there are `tensorflow` errors caused by missing libraries when calculating `FVD`-scores.

## Train your own models
As stated in our paper, our overall training procedure is divided in two main stages. To enable tractable training for our input-output-dimensionality preserving invertible model we first pretrain a video autoencoding framework to obtain latent video codes with much smaller dimensionality than the original videos. After that we train our conditional invertible generative model on these compressed video representations.

For logging our runs we used and recommend [wandb](https://wandb.ai/). Please create a free account and add your username to the config. During training of both our video autoencoding (first stage) and invertible models (second stage) we save those checkpoints with the smallest `FVD`-score during evaluation. As the original `FVD` implementation only available in `tensorflow`, we created a custom `pytorch` `FVD`-model which we use during training (for evaluation, we use the [original implementation](https://github.com/google-research/google-research/tree/master/frechet_video_distance)). The copmuted scores do not coincide with the original ones but the are strongly correlated. Therefore, this metric serves well when intending to optimize the model wrt. `FVD`. 

### Video autoencoding model

To train our video autoencoding model run the following command

```shell script
python -W ignore main.py --config config/first_stage.yaml --gpus <GPU_ID> --model_name <MODEL_NAME>
```

The used train data, model architecture and video resolution can be specified in `config/first_stage.yaml`. The the comments for an explanantion of the parameters.

If you have trained such a model and want to use it for subsequent training of our [invertible second stage model](#invertible-generative-model) you can add it to the `first_stage_models`-dict in the file `models/pretrained_models.py` by simply specifying the `<MODEL_NAME>` and the path to the checkpoint-file want to use.
### Invertible generative model

Our conditional invertible model can be trained via the command

```shell script
python -W ignore main.py --config config/second_stage.yaml --gpus <GPU_ID> --model_name <MODEL_NAME>
```

Again, the respective parameters to define the data and model hyperparameters can be specified in the config file `config/second_stage.yaml`. We also provide config files to train with the exact parameters which were used for our pretrained models. These files can be found in `config/pretrained_models/`. 

As our invertible models rely on pretrained networks ([video autoencoding models](#video-autoencoding-model) as well as encoders for the [source image](#source-image-encoder) `x_0` and the [poke](#poke-encoder) `c`) you have to specify these models in the config. We provide all such pretrained models on all considered datasets for video resolutions `64X64` and `128X128`. These are automatically selected based on the keys specified in the config files when starting the models. All available pretrained models and their keys can be found and expanded in `models/pretrained_models.py`. 

### Poke encoder

To train a new poke encoder, run the following command

```shell script
python -W ignore main.py --config config/poke_encoder.yaml --gpus <GPU> --model_name <MODEL_NAME>
```

As for our video autoencoding framework, you cann add your final trained model to the respective `poke_embedder`-dict in `models/pretrained_models.py`.

### Source image encoder

To train a new poke encoder, run the following command

```shell script
python -W ignore main.py --config config/img_encoder.yaml --gpus <GPU> --model_name <MODEL_NAME>
```

As for our video autoencoding framework, you cann add your final trained model to the respective `conditioner`-dict in `models/pretrained_models.py`.

### cVAE baseline

Finally we also provide code to train the cVAE baseline which we used in the ablation study in our paper. To train such a model, run

```shell script
python -W ignore main.py --config config/baseline_vae.yaml --gpus <GPU> --model_name <MODEL_NAME>
```

## Shout-outs

Thanks to everyone who makes their code and models available. In particular,

- The [Wolf](https://github.com/XuezheMax/wolf) library, from where we borrowed the basic operations for our masked convolutional normalizing flow implementation
- Our 3D encoder and discriminator are based on [3D-Resnet](https://github.com/tomrunia/PyTorchConv3D) and spatial discriminator is adapted from [PatchGAN](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix)
- The deep features based metrics which were used: [LPIPS](https://github.com/richzhang/PerceptualSimilarity) and [FVD](https://github.com/google-research/google-research/tree/master/frechet_video_distance)


## BibTeX

```
@misc{blattmann2021ipoke,
      title={iPOKE: Poking a Still Image for Controlled Stochastic Video Synthesis}, 
      author={Andreas Blattmann and Timo Milbich and Michael Dorkenwald and Björn Ommer},
      year={2021},
      eprint={2107.02790},
      archivePrefix={arXiv},
      primaryClass={cs.CV}
}
```
