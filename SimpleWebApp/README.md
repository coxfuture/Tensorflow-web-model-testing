# Tensorflow Model Testing Webapp

This is a flask webapp for testing tensorflow models. It uses opencv to stream the processed video and draw boxes around the objects you have defined for detection.

It's designed for a use case where you develop your models and write code on a local machine, but your GPU compute is done on a headless remote server. To use it, I recommend using an RTSP stream link, although local files and webcams are also supported, provided they are on the remote server. 
