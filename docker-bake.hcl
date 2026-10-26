# Release build: publishes tymxqo/nerium:v<VERSION> and :latest for both
# architectures, so multi-arch is the default rather than a flag to remember.
#
#   VERSION=$(sed -n 's/^__version__ = "\(.*\)"/\1/p' nerium/__version__.py) \
#   GIT_COMMIT=$(git rev-parse HEAD) \
#   docker buildx bake --push

variable "VERSION" {
  validation {
    condition     = VERSION != ""
    error_message = "Set VERSION to the release being published, e.g. VERSION=0.15.2."
  }
}

variable "GIT_COMMIT" {
  default = ""
}

group "default" {
  targets = ["nerium"]
}

target "nerium" {
  context   = "."
  platforms = ["linux/amd64", "linux/arm64"]
  args = {
    GIT_COMMIT = GIT_COMMIT
  }
  tags = [
    "tymxqo/nerium:v${VERSION}",
    "tymxqo/nerium:latest",
  ]
}
