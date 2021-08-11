# muppet
Incompetent version of puppet

# introduction
Will install/remove packages and create files while attempting to be idempotent.

# requirements
python3, ubuntu 18.04
Input is a yaml file.

# quick start

```
sudo python3 [operation] [input yaml]
```

supported operations
```
write_file: To create files in specific location on a linux box.
package: To install or remove packages
```
```
sudo python3 package /opt/mnt/package.yaml
```
 
yaml file structure is similar to cloud-init yaml
The yaml file works with two main keys: write_file and package.
The yaml structure looks as below, all the fields are mandatory and one can install multiple files/packages using a single yaml input file.

```
write_file:
  - path: /opt/slack/create/content.php
    permissions: "0644"
    owner: 'apache2' 
    group: 'apache2'
    content: | 
          <?php 
          header("Content-Type: text/plain"); 
          echo "Hello, world!\n";
    runcmd: echo "hello"

package:
   - name: "apache2"
     action: "install" 
     version: "2.4.29-1ubuntu4.16"
     runcmd: echo "hello"
```

# caveats/improvements required
Handling dependencies of packages.
Handling dependencies between tasks.

