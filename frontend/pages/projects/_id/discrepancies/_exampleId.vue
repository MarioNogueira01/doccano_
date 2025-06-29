<template>
  <v-card>
    <v-card-title>
      <v-btn icon @click="$router.back()">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <span class="ml-2 font-weight-medium">Discussão do Exemplo #{{ exampleId }}</span>
      <v-spacer />
    </v-card-title>
    <v-card-text>
      <div v-if="loading" class="text-center pa-10">
        <v-progress-circular indeterminate color="primary" />
      </div>

      <div v-else>
        <!-- Texto original -->
        <v-card outlined class="mb-6 pa-4">
          <h3 class="subtitle-1 mb-2">Texto Original</h3>
          <p style="white-space: pre-wrap">{{ example?.text }}</p>
        </v-card>

        <!-- Painel de Discussão -->
        <v-card outlined>
          <h3 class="subtitle-1 pa-4 pb-0">Discussão</h3>
          <!-- Filtro por anotador -->
          <v-row class="px-4 pt-2" align="center">
            <v-select
              v-model="selectedAnnotator"
              :items="annotatorOptions"
              label="Filtrar por anotador"
              dense
              hide-details
              outlined
              style="max-width: 200px"
            />
          </v-row>
          <v-list dense two-line class="py-0">
            <v-list-item v-for="c in filteredComments" :key="c.id">
              <v-list-item-content>
                <v-list-item-title
                  :style="{ color: getUserColor(c.username) }"
                >
                  {{ c.username }}
                </v-list-item-title>
                <v-list-item-subtitle>{{ c.text }}</v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action-text class="grey--text text-caption">
                {{ formatTime(c.createdAt) }}
              </v-list-item-action-text>
            </v-list-item>
          </v-list>
          <v-divider />
          <v-card-actions>
            <v-text-field
              v-model="newComment"
              label="Adicionar comentário..."
              dense
              hide-details
              outlined
              class="flex-grow-1"
              @keyup.enter="sendComment"
            />
            <v-btn icon :disabled="!newComment" @click="sendComment">
              <v-icon>mdi-send</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </div>
      <!-- Snackbar de erro -->
      <v-snackbar v-model="dbErrorVisible" :timeout="4000" color="error" top>
        {{ dbErrorMessage }}
        <v-btn text @click="dbErrorVisible = false">Fechar</v-btn>
      </v-snackbar>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapGetters } from 'vuex'
import ApiService from '@/services/api.service'

export default {
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],
  async asyncData({ params, error }) {
    const projectId = params.id
    const exampleId = params.exampleId
    try {
      const url = `/projects/${projectId}/examples/${exampleId}`
      const resp = await ApiService.get(url)
      return {
        projectId,
        exampleId,
        example: resp.data,
        loading: false,
        // UI / Annotations state
        labelOptions: [],
        selectedLabelId: null,
        annotations: [],
        groupedByLabel: {},
        comments: [],
        newComment: '',
        dbErrorVisible: false,
        dbErrorMessage: '',
        userColorMap: {},
        annotatorOptions: [],
        selectedAnnotator: null,
        selectedVersion: null
      }
    } catch (e) {
      error({ statusCode: 404, message: 'Exemplo não encontrado' })
    }
  },
  computed: {
    ...mapGetters('auth', ['getUsername']),
    filteredComments() {
      if (!this.selectedAnnotator || this.selectedAnnotator === 'Todos') {
        return this.comments
      }
      return this.comments.filter((c) => c.username === this.selectedAnnotator)
    }
  },
  mounted() {
    this.selectedVersion = this.$route.query.version ? Number(this.$route.query.version) : null;
    this.fetchComments()
  },
  methods: {
    async fetchComments() {
      try {
        const fetched = await this.$repositories.comment.list(
          this.projectId,
          Number(this.exampleId),
          undefined,
          this.selectedVersion ?? undefined
        )
        this.comments = fetched

        // preparar opções de anotadores
        const annotators = Array.from(new Set(this.comments.map((c) => c.username)))
        this.annotatorOptions = ['Todos', ...annotators]
        if (!this.annotatorOptions.includes(this.selectedAnnotator)) {
          this.selectedAnnotator = 'Todos'
        }

      } catch (err) {
        console.error('Failed to load comments', err)
        this.comments = []
        if (!err.response || (err.response.status && err.response.status >= 500)) {
          this.dbErrorMessage = 'Database unavailable at the moment, please try again later.'
        } else {
          this.dbErrorMessage = err.response?.data?.detail || 'Erro ao carregar comentários.'
        }
        this.dbErrorVisible = true
      }
    },
    formatTime(iso) {
      return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    },
    async sendComment() {
      if (!this.newComment) return
      try {
        const newComment = await this.$repositories.comment.create(
          this.projectId,
          Number(this.exampleId),
          this.newComment,
          undefined,
          this.selectedVersion ?? undefined
        )
        this.comments.push(newComment)
        // Se o novo comentador não estiver nas opções, adicionar
        if (!this.annotatorOptions.includes(newComment.username)) {
          this.annotatorOptions.push(newComment.username)
        }
        this.newComment = ''
      } catch (err) {
        console.error('Failed to send comment', err)
        if (!err.response || (err.response.status && err.response.status >= 500)) {
          this.dbErrorMessage = 'Database unavailable at the moment, please try again later.'
        } else {
          this.dbErrorMessage = err.response?.data?.detail || 'Erro ao enviar comentário.'
        }
        this.dbErrorVisible = true
      }
    },
    getUserColor(username) {
      // Returns (and assigns if necessary) a unique color for the given username
      if (!username) return 'grey'
      if (!this.userColorMap[username]) {
        const palette = [
          '#e57373', // red lighten-2
          '#64b5f6', // blue lighten-2
          '#81c784', // green lighten-2
          '#b39ddb', // deep-purple lighten-2
          '#7986cb', // indigo lighten-2
          '#4dd0e1', // cyan lighten-2
          '#f06292', // pink lighten-2
          '#ffd54f', // amber lighten-2
          '#4db6ac', // teal lighten-2
          '#a1887f', // brown lighten-2
          '#90a4ae'  // blue-grey lighten-2
        ]
        const index = Object.keys(this.userColorMap).length % palette.length
        this.userColorMap[username] = palette[index]
      }
      return this.userColorMap[username]
    }
  }
}
</script>

<style scoped>
.subtitle-1 {
  font-weight: 500;
}

.clickable-chip {
  cursor: pointer;
}
</style> 