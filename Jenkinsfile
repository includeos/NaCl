pipeline {
  agent { label 'ubuntu-18.04' }

  environment {
    CONAN_USER_HOME = "${env.WORKSPACE}"
    PROFILE_x86_64 = 'clang-6.0-linux-x86_64'
    PROFILE_x86 = 'clang-6.0-linux-x86'
    CPUS = """${sh(returnStdout: true, script: 'nproc')}"""
    CC = 'clang-6.0'
    CXX = 'clang++-6.0'
    PACKAGE = 'NaCl'
    USER = 'includeos'
    CHAN = 'test'
    REMOTE = "${env.CONAN_REMOTE}"
    BINTRAY_CREDS = credentials('devops-includeos-user-pass-bintray')
  }

  stages {
    stage('Setup') {
      steps {
        sh script: "conan config install https://github.com/includeos/conan_config.git", label: "conan config install"
      }
    }
    stage('Pull Request pipeline') {
      when { changeRequest() }
      stages {
        stage('Build package') {
          steps {
            build_conan_package("$PROFILE_x86_64")
          }
        }
      }
    }
    stage('Deploy package pipeline') {
      when {
        anyOf {
          branch 'master'
        }
      }
      stages {
        stage('Build Conan package') {
          steps {
            //TODO foreach profile ?
            build_conan_package("$PROFILE_x86_64")
          }
        }
        stage('Upload to bintray') {
          steps {
            sh script: """
              conan user -p $BINTRAY_CREDS_PSW -r $REMOTE $BINTRAY_CREDS_USR
              VERSION=\$(conan inspect -a version . | cut -d " " -f 2)
              conan upload --all -r $REMOTE $PACKAGE/\$VERSION@$USER/$CHAN
            """, label: "Upload to bintray"
          }
        }
      }
    }
  }
  post {
    cleanup {
      sh script: """
        VERSION=\$(conan inspect -a version . | cut -d " " -f 2)
        conan remove $PACKAGE/\$VERSION@$USER/$CHAN -f || echo 'Could not remove. This does not fail the pipeline'
      """, label: "Cleaning up and removing conan package"
    }
  }
}


def build_conan_package(String profile) {
  sh script: "conan create . $USER/$CHAN -pr ${profile}", label: "Build with profile: $profile"
}
