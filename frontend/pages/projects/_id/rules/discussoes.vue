<template>
  <v-card class="pa-4" height="100%">
    <v-card-title class="d-flex align-center">
      Discussões
      <v-spacer />
      <v-btn color="primary" @click="openCreateDialog">Criar Discussão</v-btn>
      <v-btn color="secondary" class="ml-2" @click="$router.back()">Voltar</v-btn>
    </v-card-title>
    <v-divider></v-divider>
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
              <v-list-item-title class="caption grey--text">Sem discussões.</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-col>
      <v-col cols="12" md="9" class="pa-2">
        <ThreadChat
          v-if="selectedThreadId"
          :project-id="projectId"
          :thread-id="selectedThreadId"
          :thread-title="selectedThreadTitle"
          :key="`chat-${selectedThreadId}`"
        />
        <v-alert v-else type="info">Selecione uma discussão à esquerda ou crie uma nova.</v-alert>
      </v-col>
    </v-row>

    <!-- Diálogo para criar discussão -->
    <v-dialog v-model="dialogCreate" max-width="400px">
      <v-card>
        <v-card-title class="headline">Criar Nova Discussão</v-card-title>
        <v-card-text>
          <v-text-field v-model="newThreadTitle" label="Título" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="dialogCreate = false">Cancelar</v-btn>
          <v-btn color="primary" text @click="createThread">Criar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import ThreadChat from '~/components/ThreadChat.vue'
import { DiscussionThreadApplicationService } from '~/services/application/discussionThread/discussionThreadApplicationService'

export default {
  name: 'RulesDiscussoes',
  components: { ThreadChat },
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],
  data() {
    return {
      threads: [],
      selectedThreadId: null,
      selectedThreadTitle: '',
      dialogCreate: false,
      newThreadTitle: '',
      service: new DiscussionThreadApplicationService(),
    }
  },
  computed: {
    projectId() {
      return this.$route.params.id
    },
  },
  mounted() {
    this.fetchThreads()
  },
  methods: {
    async fetchThreads() {
      try {
        this.threads = await this.service.list(this.projectId)
        if (this.threads.length) {
          this.selectThread(this.threads[0])
        }
      } catch (e) {
        console.error('Erro ao buscar threads', e)
      }
    },
    selectThread(thread) {
      this.selectedThreadId = thread.id
      this.selectedThreadTitle = thread.title
    },
    openCreateDialog() {
      this.newThreadTitle = ''
      this.dialogCreate = true
    },
    async createThread() {
      if (!this.newThreadTitle.trim()) return
      try {
        const newThread = await this.service.create(this.projectId, this.newThreadTitle.trim())
        this.threads.unshift(newThread)
        this.selectThread(newThread)
        this.dialogCreate = false
      } catch (e) {
        console.error('Erro ao criar discussão', e)
      }
    },
  },
}
</script> 