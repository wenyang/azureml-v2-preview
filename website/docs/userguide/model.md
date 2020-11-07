---
title: Model
---

## Overview

Models are artifacts generated during a job or uploaded by a user. They contain both the binary artifacts which represent the model as well as instructions on how to use the model to make predictions.

At its simplest, a model is packaged code that takes an input and predicts an output. Creating a machine learning model involves selecting an algorithm and providing it with data. Training is an iterative process that produces a trained model, which encapsulates what the model learned during the training process.	

Model management and the model registry are framework agnostic when it comes to model management - you can use any popular machine learning framework, such as Scikit-learn, XGBoost, PyTorch, TensorFlow, and Chainer.

You can bring a model that was trained outside of Azure Machine Learning. Or you can train a model by submitting a [run](#runs) of an [experiment](#experiments) to a [compute target](#compute-targets) in Azure Machine Learning. Once you have a model, you [register the model](#register-model) in the workspace.	

Azure Machine Learning is framework agnostic. When you create a model, you can use any popular machine learning framework, such as Scikit-learn, XGBoost, PyTorch, TensorFlow, and Chainer.	

Registered models are identified by name and version. Each time you register a model with the same name as an existing one, the registry assumes that it's a new version. The version is incremented, and the new model is registered under the same name.	Models are identified by name and version. Each time you register a model with the same name as an existing one, the registry assumes that it's a new version. The version is incremented, and the new model is registered under the same name. 
