<template>
    <v-container fluid>
      <v-card>
        <v-card-title>
          <v-icon left color="primary">mdi-compare-multiple</v-icon>
          Multi-User Annotation Comparison
          <v-spacer></v-spacer>
          <div class="d-flex align-center">
            <v-chip
              v-for="(user, index) in selectedUsers"
              :key="user.id"
              small
              :color="getUserColor(index)"
              :text-color="getUserTextColor(index)"
              class="mr-2"
            >
              <v-avatar left size="24" class="mr-1">
                <v-icon x-small>mdi-account</v-icon>
              </v-avatar>
              {{ user.username }}
            </v-chip>
          </div>
        </v-card-title>
        <v-card-text>
          <v-alert v-if="!selectedUsers || selectedUsers.length < 2" type="error">
            Please select at least two users to compare.
          </v-alert>
          <v-progress-circular v-if="loading" indeterminate color="primary" />
          <div v-else>
            <div v-if="documents.length === 0">
              <v-alert type="info">No documents found in this project.</v-alert>
            </div>
            <div v-else>
              <!-- Show all documents with multi-user comparison -->
              <div v-for="doc in documents" :key="doc.id" class="mb-6">
                <v-card outlined>
                  <v-card-title class="py-3">
                    <v-icon left color="primary">mdi-file-document</v-icon>
                    Document #{{ doc.id }}
                    <v-spacer></v-spacer>
                    <v-chip small color="grey lighten-2">
                      {{ doc.text ? doc.text.substring(0, 50) + '...' : 'No text' }}
                    </v-chip>
                  </v-card-title>
                  <v-card-text class="pa-0">
                    <multi-user-comparison-view
                      :project-id="projectId"
                      :document-id="doc.id"
                      :selected-users="selectedUsers"
                      :labels="labels"
                      :users="users"
                    />
                  </v-card-text>
                </v-card>
              </div>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-container>
  </template>
  
  <script lang="ts">
  import Vue from 'vue'
  import MultiUserComparisonView from '@/components/annotations/MultiUserComparisonView.vue'
  
  export default Vue.extend({
    components: { MultiUserComparisonView },
    layout: 'project',
    async asyncData({ $services, $repositories, params, query, store }) {
      const projectId = params.id
      const userIds = query.users ? query.users.split(',').map(id => parseInt(id)) : []
      console.log('Compare page - User IDs from query:', userIds)
      
      let documents = []
      let labels = []
      let users = []
      let selectedUsers = []
      try {
        documents = (await $services.example.list(projectId, {})).items || []
        const project = await store.getters['projects/project']
        labels = project && project.labels ? project.labels : []
        users = await $repositories.member.list(projectId)
        console.log('Compare page - All users from member list:', users)
        console.log('Compare page - User IDs to filter by:', userIds)
        
        selectedUsers = users.filter(user => userIds.includes(user.user))
        console.log('Compare page - Selected users after filtering:', selectedUsers)
      } catch (e) {
        console.error('Compare page - Error loading data:', e)
        // handle error
      }
      return { projectId, 
        userIds, documents, labels, users, selectedUsers, loading: false }
    },
    data() {
      return { loading: false }
    },
    methods: {
      getUserColor(index: number): string {
        const colors = ['#fff3e0', '#e3f2fd', '#f3e5f5', '#e8f5e8', '#fff8e1', '#fce4ec']
        return colors[index % colors.length]
      },
      getUserTextColor(index: number): string {
        const colors = ['#e65100', '#0d47a1', '#4a148c', '#1b5e20', '#f57f17', '#880e4f']
        return colors[index % colors.length]
      }
    }
  })
  </script> 