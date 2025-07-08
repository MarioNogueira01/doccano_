<template>
  <v-card class="pa-4">
    <v-card-title class="d-flex align-center">
      Histórico de Discussões
      <v-spacer />
      <v-select
        v-model="selectedVersionId"
        :items="versionOptions"
        label="Versão"
        outlined
        dense
        style="max-width: 200px"
        @change="fetchThreads"
      />
      <v-btn color="secondary" class="ml-2" @click="$router.back()">Voltar</v-btn>
    </v-card-title>

    <v-row no-gutters>
      <v-col cols="12" md="3" class="pa-2">
        <v-list dense nav>
          <v-list-item
            v-for="thread in threads"
            :key="thread.id"
            :active="thread.id === selectedThreadId"
            @click="selectThread(thread)"
          >
            <v-list-item-content>
              <v-list-item-title>{{ thread.title }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item v-if="threads.length === 0">
            <v-list-item-content>
              <v-list-item-title class="caption grey--text">
                Sem discussões nesta versão.
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-col>
      <v-col cols="12" md="9" class="pa-2">
        <ThreadChat
          v-if="selectedThreadId"
          :project-id="$route.params.id"
          :thread-id="selectedThreadId"
          :thread-title="selectedThreadTitle"
          :read-only="true"
          :key="`chath-${selectedThreadId}`"
        />
        <v-alert v-else type="info">Selecione uma discussão.</v-alert>
      </v-col>
    </v-row>
  </v-card>
</template>

<script>
import ThreadChat from '~/components/ThreadChat.vue'
import {
  DiscussionThreadApplicationService,
} from '~/services/application/discussionThread/discussionThreadApplicationService'
export default {
  components: { ThreadChat },
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],
  data() {
    return {
      versions: [],
      selectedVersionId: null,
      threads: [],
      selectedThreadId: null,
      selectedThreadTitle: '',
      service: new DiscussionThreadApplicationService(),
    }
  },
  computed: {
    versionOptions() {
      return this.versions.map(v => ({ text: `Versão ${v.version}`, value: v.id }))
    }
  },
  async mounted() {
    await this.fetchVersions()
  },
  methods: {
    async fetchVersions() {
      try {
        const res = await this.$services.project.listVersions(this.$route.params.id)
        const versionsData = Array.isArray(res) ? res : (res.versions || [])
        this.versions = versionsData.filter(v => v.status === 'closed')
        if (this.versions.length) {
          this.selectedVersionId = this.versions[0].id
          await this.fetchThreads()
        }
      } catch (e) {
        console.error('Erro ao buscar versões:', e)
      }
    },
    async fetchThreads() {
      if (!this.selectedVersionId) return
      try {
        this.threads = await this.service.list(this.$route.params.id, this.selectedVersionId)
        if (this.threads.length) {
          this.selectThread(this.threads[0])
        } else {
          this.selectedThreadId = null
        }
      } catch (e) {
        console.error('Erro ao buscar threads:', e)
      }
    },
    selectThread(thread) {
      this.selectedThreadId = thread.id
      this.selectedThreadTitle = thread.title
    },
  }
}
</script> 