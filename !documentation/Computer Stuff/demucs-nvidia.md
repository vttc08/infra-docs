---
date: 2022-12-23T00:32:00.000000Z
update: 2022-12-24T22:07:56-07:00
comments: "true"
---
# Demucs Nvidia

Demucs is an music separation tool that has potential for a karaoke setup.

[https://github.com/facebookresearch/demucs](https://github.com/facebookresearch/demucs)

[https://www.youtube.com/watch?v=9QnFMKWEFcI&amp;t=585s](https://www.youtube.com/watch?v=9QnFMKWEFcI)

[https://docs.google.com/document/d/1XMmLrz-Tct1Hdb\_PatcwEeBrV9Wrt15wHB1xhkB2oiY/edit](https://docs.google.com/document/d/1XMmLrz-Tct1Hdb_PatcwEeBrV9Wrt15wHB1xhkB2oiY/edit)

**Installation on PC with Nvidia**

1. Firstly install Anaconda. Download Anaconda for Windows [https://www.anaconda.com/products/distribution](https://www.anaconda.com/products/distribution)
2. Install PyTorch. [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/). Select the correct version of pytorch.
3. Install ffmpeg. [https://www.gyan.dev/ffmpeg/builds/]](assets/gallery/2022-12/TwJimage.png)

**Demucs**

After installing the prerequesties.

Open "Anaconda terminal" and type

```shell
python.exe -m pip install -U demucs
```

```shell
pip install PySoundFile 
```

**Running Demucs**

```shell
demucs "C:\path\to\music\file.mp3"
```

This will run demucs with CUDA GPU acceleration, make sure to put the path in double quote. The extracted file will be found in the directory where you run the command eg. the default Anaconda prompt starts in ~/separated