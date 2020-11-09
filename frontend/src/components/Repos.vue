<template>
  <div class="accordion" role="tablist">
      
    <b-card v-for="repo in repos" v-bind:key="repo.project" no-body class="mb-1">
      <b-card-header header-tag="header" class="p-1" role="tab">
        <b-button block v-b-toggle="repo.project" variant="info">{{ repo.project }}</b-button>
      </b-card-header>
      <b-collapse :id="repo.project" accordion="my-accordion" role="tabpanel">
        <b-card-body>
          <b-card-text>
              <b-container class="bv-example-row">
                <b-row v-for="branch in repo.branches" v-bind:key="branch" class="branch-row">
                    <b-col><div class="branch-status"></div></b-col>
                    <b-col>{{ branch }}</b-col>
                    <b-col><b-button variant="primary" @click="trigger(repo.project, branch)" class="branch-button">Build</b-button></b-col>
                </b-row>
              </b-container>             
          </b-card-text>
        </b-card-body>
      </b-collapse>
    </b-card>
  </div>
</template>

<script>
export default {
  name: 'Repos',
  data () {
    return {
      repos: [
        {
          project: 'Guslington/multibranch-codepipeline-example',
          branches: [
            'main',
            'develop',
            'feature/new'
          ]
        }
      ]
    }
  },
  methods: {
    async trigger(repo, branch) {
      this.flashMessage.info({
        message: 'Triggering pipeline ' + repo + '/' + branch,
        time: 3000
      })

      const request = new Request(
        'https://23xok0fq3f.execute-api.ap-southeast-2.amazonaws.com/Prod/triggers/pipeline',
        {
          method: 'POST',
          mode: 'cors',
          cache: 'default',
          body: JSON.stringify({Project: repo, Branch: branch})
        }
      )

      const res = await fetch(request)
      const data = await res.json()

      this.flashMessage.success({
        message: repo + '/' + branch + ' pipeline triggered with execition id ' + data.executionId,
        time: 3000
      })

      await setTimeout(console.log('waiting'), 2000)
      this.wait(repo, branch, data.executionId)
    },
    async wait(repo, branch, id) {
      const params = new URLSearchParams({
        project: repo
      })

      const request = new Request(
        'https://23xok0fq3f.execute-api.ap-southeast-2.amazonaws.com/Prod/execution/status/' + id + '?' + params,
        {
          method: 'get',
          mode: 'cors',
          cache: 'default'
        }
      )

      const res = await fetch(request)
      const data = await res.json()

      // STATES - 'InProgress'|'Stopped'|'Stopping'|'Succeeded'|'Superseded'|'Failed'
      if (data.status === 'InProgress') {
        console.log('in progress')
        await setTimeout(this.wait(repo, branch, id), 10000)
      } else if (data.status === 'Succeeded') {
        this.flashMessage.success({
          message: repo + '/' + branch + ' pipeline complete',
          time: 3000
        })
      } else if (data.status === 'Failed') {
        this.flashMessage.error({
          message: repo + '/' + branch + ' pipeline failed',
          time: 3000
        })
      } else {
        this.flashMessage.error({
          message: repo + '/' + branch + ' pfinished with state ' + data.status,
          time: 3000
        })
      }

      return true
    }
  }
}
</script>

<style>
.branch-status {
    background-color: green;
    height: 100%;
    width: 40px;
    float: right;
    border-radius: 50%;
    display: inline-block;

}
.branch-row {
    padding: 10px 0 10px 0;
}
.branch-button {
    float: left;
}
</style>