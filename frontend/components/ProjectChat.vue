<template>
  <div>
    <v-card outlined class="pa-2 mb-4">
      <v-card-title class="subtitle-2 grey--text text--darken-1">
        Discussão do Projeto
      </v-card-title>
      <v-divider></v-divider>
      <div ref="chatWindow" class="chat-window">
        <div v-for="msg in messages" :key="msg.id" class="d-flex flex-column mb-1">
          <span
            class="font-weight-bold"
            :style="{ color: getUserColor(msg.username || 'Anônimo') }"
          >
            {{ msg.username || 'Anônimo' }}
          </span>
          <span>{{ msg.message }}</span>
          <span class="caption grey--text">{{ formatDate(msg.created_at) }}</span>
        </div>
        <div v-if="messages.length === 0" class="caption grey--text text-center">
          Não há mensagens ainda.
        </div>
      </div>

      <v-divider></v-divider>
      <div v-if="!readOnly" class="d-flex align-center mt-2">
        <v-text-field
          v-model="newMessage"
          label="Digite sua mensagem..."
          outlined
          dense
          hide-details
          class="flex-grow-1 mr-2"
          :disabled="loading"
          @keyup.enter="sendMessage"
        />
        <v-btn
          color="primary"
          :disabled="!newMessage.trim() || loading"
          :loading="loading"
          @click="sendMessage"
        >
          Enviar
        </v-btn>
      </div>
    </v-card>

    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="5000" top>
      {{ snackbarText }}
      <template #action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar = false">Fechar</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
export default {
  name: 'ProjectChat',
  props: {
    projectId: { type: [String, Number], required: true },
    versionId: { type: [String, Number], default: null },
    readOnly: { type: Boolean, default: false }
  },
  data() {
    return {
      messages: [],
      newMessage: '',
      loading: false,
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'warning'
    }
  },
  mounted() {
    this.fetchMessages()
  },
  methods: {
    async fetchMessages() {
      this.loading = true
      try {
        const res = await this.$services.projectDiscussion.list(this.projectId, this.versionId)
        this.messages = res || res.messages || []
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      } catch (e) {
        console.error('Erro ao buscar mensagens', e)
        this.showError('Erro ao carregar mensagens')
      } finally {
        this.loading = false
      }
    },
    async sendMessage() {
      if (this.readOnly) return
      if (!this.newMessage.trim()) return
      const messageText = this.newMessage.trim()
      this.newMessage = ''
      this.loading = true
      try {
        const newMsg = await this.$services.projectDiscussion.create(this.projectId, messageText)
        // Caso o backend devolva a mensagem recém criada
        const pushMsg = newMsg.id
          ? newMsg
          : {
              id: Date.now(),
              message: messageText,
              username: this.$store?.state?.user?.username || 'Eu',
              created_at: new Date(),
            }
        this.messages.push(pushMsg)
        this.$nextTick(() => {
          this.scrollToBottom()
        })
        this.showSuccess('Mensagem enviada com sucesso!')
      } catch (e) {
        console.error('Erro ao enviar mensagem', e)
        const errorMessage = 'Erro ao enviar mensagem. Por favor, tente novamente.'
        this.showError(errorMessage)
        this.newMessage = messageText
      } finally {
        this.loading = false
      }
    },
    showError(message) {
      this.snackbarText = message
      this.snackbarColor = 'error'
      this.snackbar = true
    },
    showSuccess(message) {
      this.snackbarText = message
      this.snackbarColor = 'success'
      this.snackbar = true
    },
    scrollToBottom() {
      const el = this.$refs.chatWindow
      if (el && el.scrollTo) {
        el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
      }
    },
    formatDate(d) {
      const date = new Date(d)
      return date.toLocaleString()
    },
    getUserColor(username) {
      const colors = [
        '#FF0000', '#00A0FF', '#00FF00', '#FF00FF', '#FFA500',
        '#9400D3', '#008080', '#FF4500', '#FFD700', '#4B0082',
        '#800000', '#00FFFF', '#8B4513', '#000000', '#708090'
      ]
      let hash = 0
      for (let i = 0; i < username.length; i++) {
        hash = ((hash << 5) - hash) + username.charCodeAt(i)
        hash |= 0
      }
      const index = Math.abs(hash) % colors.length
      return colors[index]
    }
  }
}
</script>

<style scoped>
.chat-window {
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
}
</style> 