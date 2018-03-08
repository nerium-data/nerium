# OAO Nerium Deployment

Note: Insofar as we are committed to maintaining this as a public project, it should be noted that this document is specific to OAO deployment usage, and others may disregard it.

## Deploy Front End for Development

### Prerequisites

You must be a member of the OAO team in Keybase and have access to the
`oao/secrets` encrypted git repository.

You must also have appropriate permissions in the google cloud project,
lexical-cider-93918 at the time of this writing. Though in order for this
project to be public that'll need to change.

The deployment also depends on a few tools

* Make
* kubectl
* gcloud

### Procedure

1. As a team, choose a cluster name for the following steps. For example,
   let's say the team has chosen `sarcastic-skateboard-72` as a cluster
   name.

2. Set the `CLUSTER` envar to that name

   `export CLUSTER=sarcastic-skateboard-72`

3. Clone (or pull) the most recent secrets from the `oao/secrets` encrypted
   repository somewhere out of the way. Note the path. For example, let's
   say you cloned that into your home directory.

4. Set the SECRET_PATH envar to that path.

   `export SECRET_PATH=$HOME/secrets`

5. Deploy Front End.

   `make deploy`

   a. If the cluster already exists, this command will use it. Otherwise, it
      will ask whether to create the cluster on your behalf.

## Deploy Front End for Permanent Deployments

Permanent deployments have not been finalized as of Feb 28 2018, but they would
be something like `integration`, `stage`, and `production`.

* Permanent deployments are initially deployed using the dev instructions above

* CI servers watching for tags that match their environment (integration, stage,
  production) and will then simply swap in the new image to the deployment that
  was deployed with the dev instructions.

  * Set this up in [cloud builder](https://console.cloud.google.com/gcr/triggers)
    * triggering off a tag that matches `^(integration|stage|production)$`
    * configured by `cloudbuild.yaml` located at `/cloudbuild.yaml`
    * with no substitution variables

* This may be an interim solution until we get experience with permanent
  deployments in this paradigm.