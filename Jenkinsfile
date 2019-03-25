pipeline {
  agent { label 'ubuntu-18.04' }

  triggers {
    upstream(
      upstreamProjects: 'hioa-cs-org-test/IncludeOS/dev', threshold: hudson.model.Result.SUCCESS
      )
  }

  options {
    checkoutToSubdirectory('src')
  }

  environment {
    CONAN_USER_HOME = "${env.WORKSPACE}"
    PROFILE_x86_64 = 'clang-6.0-linux-x86_64'
    CPUS = """${sh(returnStdout: true, script: 'nproc')}"""
    CC = 'clang-6.0'
    CXX = 'clang++-6.0'
    PACKAGE = 'NaCl'
    USER = 'includeos'
    CHAN = 'default'
    REMOTE = "${env.CONAN_REMOTE}"
    BINTRAY_CREDS = credentials('devops-includeos-user-pass-bintray')
    SRC = "${env.WORKSPACE}/src"
  }

  stages {
    stage('Conan channel') {
      parallel {
        stage('Pull request') {
          when { changeRequest() }
          steps { script { CHAN = 'test' } }
        }
        stage('Master merge') {
          when { branch 'master' }
          steps { script { CHAN = 'latest' } }
        }
        stage('Stable release') {
          when { buildingTag() }
          steps { script { CHAN = 'stable' } }
        }
      }
    }
    stage('Setup') {
      steps {
        sh script: "ls -A | grep -v src | xargs rm -r || :", label: "Clean workspace"
        sh script: "conan config install https://github.com/includeos/conan_config.git", label: "conan config install"
      }
    }
    stage('Build package') {
      steps {
        build_conan_package("$PROFILE_x86_64")
      }
    }
    stage('Upload to bintray') {
      when {
        anyOf {
          branch 'master'
          buildingTag()
        }
      }
      steps {
        sh script: """
          conan user -p $BINTRAY_CREDS_PSW -r $REMOTE $BINTRAY_CREDS_USR
          VERSION=\$(conan inspect -a version $SRC | cut -d " " -f 2)
          conan upload --all -r $REMOTE $PACKAGE/\$VERSION@$USER/$CHAN
          """, label: "Upload to bintray"
      }
    }
  }
}

def build_conan_package(String profile) {
  sh script: "conan create $SRC $USER/$CHAN -pr ${profile}", label: "Build with profile: $profile"
}
