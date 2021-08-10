import apt

apt_cache = apt.Cache() #High level

apt_cache.update()
apt_cache.open()

list_pkgs = []

package_name = 'apache2'
#for package_name in apt_cache.keys():
selected_package = apt_cache[package_name]

#Verify that the package can be upgraded
if selected_package.isUpgradable:
  pkg = dict(
        name=selected_package.name,
        version= selected_package.installedVersion,
        desc= selected_package.description,
        homepage= selected_package.homepage,
        severity= selected_package.priority)
  list_pkgs.append(pkg)

print list_pkgs
