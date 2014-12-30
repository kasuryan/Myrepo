class webconfig (
        $dropbox = extlookup('dropbox'),
        $dburl,
        $rlydb_username,
        $rlydb_passwd,
        $rlycomponent_dsn,
        $bindtoip,
        $webconfig_instance,
)
        {
$jdk_dir="/usr/java"
#$jdk_ver="jdk1.6.0_26"
#$jdk_bin="jdk-6u26-linux-x64.bin"
$tomcat_pkg="apache-tomcat-6.0.29.tar.gz"
$tomcat_home="/usr/local/apache-tomcat"

$ldap_array = split(extlookup('ldap_uri')," ")
$ldap_url = $ldap_array[0]
###SET BELOW VARIABLE to 'true' WHEN THERE IS A NEW WEBCONFIGURE.WAR pkg available in the banana repos.
$update=''

realize Package['jdk']

file {'/etc/sysconfig/tomcat':
        ensure          => file,
        source          => "puppet:///modules/webconfig/tomcat_sysconfig",
        }
file {'/etc/init.d/tomcat':
        ensure          => file,
        source          => "puppet:///modules/webconfig/tomcat",
        mode            => 0755,
        }

exec {"${tomcat_pkg} install":
        command         => "wget ${dropbox}/webconfig/${tomcat_pkg} -q -O - | tar zxf -",
        cwd             => "/usr/local",
        creates         => "/usr/local/apache-tomcat-6.0.29",
        provider        => shell,
        user            => root,
        require         => File['/etc/sysconfig/tomcat'],
        }
file {"${tomcat_home}":
        ensure          => link,
        target          => "/usr/local/apache-tomcat-6.0.29",
        require         => Exec["${tomcat_pkg} install"],

        }
if $update == 'true'
        {
        exec {"cleanup Webconfig":
                command         => "/etc/init.d/tomcat stop; sleep 5; rm -fr /usr/local/apache-tomcat/work/Catalina/localhost; rm -fr ${webconfig_instance} *.war",
                cwd             => "${tomcat_home}/webapps",
                provider        => shell,
                user            => root,
                returns         => 0,
                require         => [File["${tomcat_home}"],File['/etc/init.d/tomcat'],Exec["${tomcat_pkg} install"]]
                }

        exec {"WebConfigure.war":
                command         => "wget ${dropbox}/webconfig/WebConfigure.war -q; mv WebConfigure.war ${webconfig_instance}.war",
                creates         => "${tomcat_home}/webapps/${webconfig_instance}.war",
                cwd             => "${tomcat_home}/webapps",
                provider        => shell,
                user            => root,
                require         => [File["${tomcat_home}"],File['/etc/init.d/tomcat'],Exec["${tomcat_pkg} install"],Exec['cleanup Webconfig']],
                }

        exec {"WebConfigure":
                command         => "/etc/init.d/tomcat start; sleep 30",
                creates         => "${tomcat_home}/webapps/${webconfig_instance}",
                cwd             => "/",
                provider        => shell,
                user            => root,
                returns         => 0,
                require         => Exec["WebConfigure.war"],
                }
        }
else
        {
        exec {"WebConfigure.war":
                command         => "wget ${dropbox}/webconfig/WebConfigure.war -q;mv WebConfigure.war ${webconfig_instance}.war",
                creates         => "${tomcat_home}/webapps/${webconfig_instance}.war",
                cwd             => "${tomcat_home}/webapps",
                provider        => shell,
                user            => root,
                require         => [File["${tomcat_home}"],File['/etc/init.d/tomcat'],Exec["${tomcat_pkg} install"]],
        }

        exec {"WebConfigure":
                command         => "/etc/init.d/tomcat start; sleep 30",
                creates         => "${tomcat_home}/webapps/${webconfig_instance}",
                cwd             => "/",
                provider        => shell,
                user            => root,
                returns         => 0,
                require         => Exec["WebConfigure.war"],
                }
        }

service {'tomcat':
        ensure          => running,
        hasstatus       => false,
        status          => "ps ax | grep -i tomcat | grep -v grep",
        hasrestart      => false,
        restart         => "/etc/init.d/tomcat stop; sleep 20; /etc/init.d/tomcat start",
        start           => "/etc/init.d/tomcat start",
        require         => [Exec["${tomcat_pkg} install"],Exec["WebConfigure"]],
        }

exec {"keystore password":
        command         => "echo -e \"webconfig\\nwebconfig\\n\\n\\n\\n\\n\\n\\nyes\\n\\n\" | ${jdk_dir}/default/bin/keytool -genkey -alias tomcat -keyalg RSA",
        creates         => "/root/.keystore",
        provider        => shell,
        user            => root,
        }

file {"${tomcat_home}/conf/server.xml":
        ensure          => file,
        content         => template('webconfig/server.xml.erb'),
        mode            => 0600,
        owner           => root,
        require         => Exec["${tomcat_pkg} install"],
        notify          => Service['tomcat'],
        }
file {"${tomcat_home}/webapps/${webconfig_instance}/WEB-INF/web.xml":
        ensure          => file,
        source          => "puppet:///modules/webconfig/web.xml",
        mode            => 0600,
        owner           => root,
        require         => Exec["WebConfigure"],
        notify          => Service['tomcat'],
        }

file {"${tomcat_home}/webapps/${webconfig_instance}/WEB-INF/classes/webconfigure.properties":
        ensure          => file,
        content         => template('webconfig/webconfigure.properties.erb'),
        mode            => 0600,
        owner           => root,
        require         => Exec["WebConfigure"],
        notify          => Service['tomcat'],
        }

}
