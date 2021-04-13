# Getting Set Up

## Install the CLI


```bash
pip install determined-cli
```

## Point the CLI to the cluster

```bash
export DET_MASTER=ec2-54-163-80-48.compute-1.amazonaws.com
```
#### To Test
```bash
det experiment list
```

This can be shortened to `det e list`

## Log In To The Cluster

Everyone who registered has a user created for them in the cluster. 

The username is their registered name with the spaces replaced with underscores. (punctuation removed)

There is no password. Reach out on Slack if you don't know what your username is or if you can't log in.

#### Web UI

The Web UI is available at http://ec2-54-163-80-48.compute-1.amazonaws.com:8080/

#### CLI

```
det user login YOUR_USERNAME
```

To confirm that this worked, run

```
det user whoami
```

## Download model to train
```
git clone https://github.com/armandmcqueen/dtrain-lnl
```

## Test that you can train

By training with the fast.yaml configuration. Make sure you are in the `cifar10_pytorch/` directory

```
det e create -f fast.yaml .
```

You should see training logs start to appear in your terminal. The experiment should also appear in the Experiment list in the WebUI.

You can filter the WebUI to only show experiments that you created.

#### Explanation of the above command

This is creating an experiment. It is uploading all code in the current directory (most importantly the `model_def.py`). It is configuring the experiment with the `fast.yaml` experiment configuration, which runs training very briefly. The `-f` flag tells the CLI to tail the logs once the experiment has begun. 
