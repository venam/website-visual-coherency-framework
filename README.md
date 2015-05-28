Website Visual Coherence Framework
----------------------------------


A Framework (bunch of tools) to check the coherency of a website through time
or throughout the internal pages.


## The Tools


### Firefox Addon


The `scrotter_addon` dir contains an addon (Firefox) which role is to 
automatically browse through a series of webpage, take a fullpage screenshot 
of them, and save it in a sub-dir (the name is the current date) of a 
directory you specify.


Preferably, this directory is the `perceptual_comparison/scrotter_outputs` dir.


Over time you'll accumulate a lot of subdirs with screenshots of the websites
you care about.


TODO: Use phantomjs to take the screenshots instead of the addon.
I wrote the addon just to learn how to create one.


### Image Comparison


Now that you have a bunch of images you can compare them using perceptual hash.
In the `perceptual_comparison` the `main.py` program can be used to do so.


Use the --compare option:
```
  -c, --compare [type] [arg] Compare directory depending on the type:
     the type can be "external" or "internal"
     for "internal" you have to specify one directory
     for "external you have to specify two directories
```

The result will be saved in an sqlite3 database for later use in the report
generation.


An internal comparison is a comparison within the same directory.
For example, if you've taken screenshots of a full site-map of your website and
it was saved in a dir name `dir_name` the internal comparison will compare how
the screenshots are visually close/related to each others.

An external comparison is a comparison between two different directories.
It will compare the images that have the same name.


Note: Only .jpeg files are supported at the moment


Example:

```
python2 main.py -c internal scrotter_outputs/2014_8_28_18_21_11
```


### Report Generation


the `main.py` script in the `perceptual_comparison` directory can also be used
to generate report webpage of the image comparison that has been done.


Use the --report option:
```
  -r, --report [type] [name] [number]
     generate a report of type [type] with the name
     [name] compose of less than [number] of sections
     the type can be "external" or "internal"
```

The reports will then be saved under the `reports` directory.


Here's an example of what a report can look like:

```
python2 main.py -c internal scrotter_outputs/2014_8_28_18_21_11
```

![example internal report](http://pub.iotek.org/p/MZvI5Ri.png)
![example external report](http://pub.iotek.org/p/KyNum2w.png)


### Complete Automation


It would be nice to completely automate all this process.
To do so Firefox should be started automatically, always using the same size
`firefox -width x -height y` , the addon should directly start it's procedure,
and the comparison and report generation should be automatic with the most
recent directory created.

This section is still a work in progress.


### Dependencies


libphash
py-phash
imagemagick
addon-sdk
