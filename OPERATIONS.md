# Deploying Nerium

## Deploy Nerium for Development

### Prerequisites

You must be a member of the OAO team in Keybase and have access to the
`oao/secrets` encrypted git repository.

You must also have appropriate permissions in the google cloud project,
lexical-cider-93918 at the time of this writing. Though in order for this
project to be public that'll need to change.

The deployment also depends on a few tools:

* Make
* kubectl
* gcloud

### Procedure

1. Choose, with the team, a cluster to deploy to. For this document, as an
   example, let's say the team has chosen `sarcastic-skateboard-72` as a cluster
   name.
1. Set the `CLUSTER` envar to that name

    `$ export CLUSTER=sarcastic-skateboard-72`

1. Clone (or pull) the most recent secrets from the `oao/secrets` encrypted
   repository somewhere out of the way. Note the path. For this document, as an
   example let's say you cloned that into your home directory.

1. Set the SECRET_PATH envar to that path.

    `$ export SECRET_PATH=$HOME/secrets`

1. Deploy Nerium.

    `$ make deploy`

  a. If the cluster already exists it will use it, otherwise it will ask if you
     would like to create it.

## Deploy Nerium for permanent deployments

Permanent deployments have not been finalized as of 2018-02-28, but they would
be something like `integration`, `stage`, and `production`.

* Permanent deployments are initially deployed using the dev instructions above
* CI servers watching for tags that match their environment (integration, stage,
  production) and will then simply swap in the new image to the deployment that
  was deployed with the dev instructions.
* This may be an interim solution until we get experience with permanent
  deployments in this paradigm.