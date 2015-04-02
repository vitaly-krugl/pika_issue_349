$PROJECT_DIR = "/vagrant"

exec { "apt-get-update":
    command => "apt-get update",
    path => "/usr/bin"
}

exec { "apt-fix-missing":
    command => "apt-get install --fix-missing",
    path => "/usr/bin",
    require => Exec["apt-get-update"]
}

exec { "pip-install-requirements":
    command => "pip install -r $PROJECT_DIR/requirements.txt",
    path => "/usr/bin",
    cwd => "$PROJECT_DIR",
    require => Package["python-pip", "python-dev"],
    logoutput => on_failure
}

package { ["cowsay", "python-dev", "python-pip", "rabbitmq-server"]:
    ensure => installed,
    require => Exec["apt-get-update", "apt-fix-missing"],
    provider => "apt"
}
