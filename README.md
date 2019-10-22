# Tensorflow Model Testing Webapp

This is a flask webapp for testing tensorflow models. It uses opencv to stream the processed video and draw boxes around the objects you have defined for detection.

It's designed for a use case where you develop your models and write code on a local machine, but your GPU compute is done on a headless remote server. To use it, I recommend using an RTSP stream link, although local files and webcams are also supported, provided they are on the remote server. 

You'll need to register an account to use it, there's not much real security but I found out how to add account management, so I did. Dummy data works fine, there's no email verification or anything.
![login page](login.png)
