<template>
    <v-container fluid>
      <v-card>
        <v-card-title>
          <v-icon left color="primary">mdi-compare</v-icon>
          Compare Annotations: {{ user1Name }} vs {{ user2Name }}
        </v-card-title>
        <v-card-text>
          <v-alert v-if="!user1Id || !user2Id" type="error">
            Please select two users to compare.
          </v-alert>
          <v-progress-circular v-if="loading" indeterminate color="primary" />
          <div v-else>
            <div v-if="documents.length === 0">
              <v-alert type="info">No documents found in this project.</v-alert>
            </div>
            <div v-else>
              <v-expansion-panels multiple>
                <v-expansion-panel v-for="doc in documents" :key="doc.id">
                  <v-expansion-panel-header>
                    Document #{{ doc.id }} - {{ doc.text ? doc.text.substring(0, 60) : 'No text' }}
                  </v-expansion-panel-header>
                  <v-expansion-panel-content>
                    <comparison-view
                      :project-id="projectId"
                      :document-id="doc.id"
                      :user1-id="user1Id"
                      :user2-id="user2Id"
                      :labels="labels"
                      :users="users"
                    />
                  </v-expansion-panel-content>
                </v-expansion-panel>
              </v-expansion-panels>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-container>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import ComparisonView from '@/components/annotations/ComparisonView.vue'
  
  export default Vue.extend({
    components: { ComparisonView },
    layout: 'project',
    async asyncData({ $services, $repositories, params, query, store }) {
      const projectId = params.id
      const user1Id = query.user1
      const user2Id = query.user2
      let documents = []
      let labels = []
      let users = []
      let user1Name = ''
      let user2Name = ''
      try {
        documents = (await $services.example.list(projectId, {})).items || []
        const project = await store.getters['projects/project']
        labels = project && project.labels ? project.labels : []
        users = await $repositories.member.list(projectId)
        user1Name = (users.find(u => u.id === user1Id) || {}).username || user1Id
        user2Name = (users.find(u => u.id === user2Id) || {}).username || user2Id
      } catch (e) {
        // handle error
      }
      return { projectId, 
        user1Id, user2Id, documents, labels, users, user1Name, user2Name, loading: false }
    },
    data() {
      return { loading: false }
    }
  })
  </script> 