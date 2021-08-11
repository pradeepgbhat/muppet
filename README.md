# muppet
An incompetent version of puppet

# introduction
Will install/remove packages and create files while attempting to be idempotent.

# requirements
python3, ubuntu 18.04
Input is a yaml file. Tries to use python3 packages already present,eliminating the need for bootstrapping script for tooling dependencies

# quick start

Requires use of sudo/root privilege
```
sudo python3 [operation] [input yaml]
```

supported operations
```
write_file: To create files in specific location on a linux box.
package: To install or remove packages
```

example for package:
```
sudo python3 package /opt/mnt/package.yaml
```

example for write_file:
```
sudo python3 write_file /opt/mnt/files.yaml
```

The package install operations have to be run first and the write_file operation.

To orchestrate start up of services or run shell scripts use runcmd option.

yaml file structure is similar to cloud-init yaml
The yaml file works with two main keys: write_file and package.

The yaml structure looks as below, all the fields are mandatory and one can install multiple files/packages using a single yaml input file.
However packages have to be installed first if we are to be modifying contents/permissions of package directories.
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
     action: "install"  #supported actions "install", "remove", "purge"
     version: "2.4.29-1ubuntu4.16" #version has to be specified, cannot use "latest" yet like puppet
     runcmd: echo "hello" #any valid shell command, could be used to restart service
```
# Example Install of Apache2 and PHP running on Ubuntu 18.04

Clone this repository on to the target system and from the repository directory execute the following commands.
 
```
1) $sudo python3 package packages.yaml
```
```
2) $sudo python3 write_file post_pkg_install_files.yaml
```
# caveats
does not handle dependencies of packages.
does not handle ordering of installation and file creation
Disable ubuntu file using runcmd if required to access publicly
