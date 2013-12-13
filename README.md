farmer
======

an async task execution app based on ansible

# First Of All !

you should deploy your [ansible](https://github.com/ansible/ansible) cluster

see: https://github.com/ansible/ansible

#Screenshot
![Screenshot](https://raw.github.com/douban/farmer/master/farmer.png)

# Running

```
git clone https://github.com/douban/farmer.git
cd farmer
python manage.py syncdb
```

in this step, you should add a user(administrator), just input your name / pass

then run it with:

```
python manage.py runserver 0.0.0.0:6969
```

view it in `http://your-domain:6969`

# Features
* async task execution with os.fork()
* re-run cmd on those failed hosts by a `retry` button
