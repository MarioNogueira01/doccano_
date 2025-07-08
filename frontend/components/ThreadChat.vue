<template>
  <div>
    <v-card outlined class="pa-2 mb-4">
      <v-card-title class="subtitle-2 grey--text text--darken-1">
        {{ threadTitle }}
      </v-card-title>
      <v-divider></v-divider>
      <div ref="chatWindow" class="chat-window">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="d-flex flex-column mb-1"
        >
          <span
            class="font-weight-bold"
            :style="{
              color: getUserColor(msg.username || 'Anônimo')
            }"
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

      <v-alert v-if="readOnly" type="info" dense text>
        Chat em modo de leitura.
      </v-alert>

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
import {
  DiscussionMessageApplicationService,
} from '~/services/application/discussionMessage/discussionMessageApplicationService'

export default {
  name: 'ThreadChat',
  props: {
    projectId: { type: [String, Number], required: true },
    threadId: { type: [String, Number], required: true },
    threadTitle: { type: String, default: 'Discussão' },
    readOnly: { type: Boolean, default: false },
  },
  data() {
    return {
      messages: [],
      newMessage: '',
      loading: false,
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'warning',
      service: new DiscussionMessageApplicationService(),
    }
  },
  mounted() {
    this.fetchMessages()
  },
  watch: {
    threadId() {
      this.fetchMessages()
    },
  },
  methods: {
    async fetchMessages() {
      this.loading = true
      try {
        const res = await this.service.list(this.projectId, this.threadId)
        this.messages = res.messages || res
        this.$nextTick(this.scrollToBottom)
      } catch (e) {
        console.error('Erro ao buscar mensagens', e)
        this.showError('Erro ao carregar mensagens')
      } finally {
        this.loading = false
      }
    },
    async sendMessage() {
      if (this.readOnly || !this.newMessage.trim()) return
      const text = this.newMessage.trim()
      this.newMessage = ''
      this.loading = true
      try {
        const newMsg = await this.service.create(this.projectId, this.threadId, text)
        const pushMsg = newMsg.id
          ? newMsg
          : {
              id: Date.now(),
              message: text,
              username: this.$store?.state?.user?.username || 'Eu',
              created_at: new Date(),
            }
        this.messages.push(pushMsg)
        this.$nextTick(this.scrollToBottom)
        this.showSuccess('Mensagem enviada!')
      } catch (e) {
        console.error('Erro ao enviar mensagem', e)
        this.showError('Erro ao enviar mensagem')
        this.newMessage = text
      } finally {
        this.loading = false
      }
    },
    showError(msg) {
      this.snackbarText = msg
      this.snackbarColor = 'error'
      this.snackbar = true
    },
    showSuccess(msg) {
      this.snackbarText = msg
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
        '#800000', '#00FFFF', '#8B4513', '#000000', '#708090',
      ]
      let hash = 0
      for (let i = 0; i < username.length; i += 1) {
        hash = ((hash << 5) - hash) + username.charCodeAt(i)
        hash |= 0 // Convert to 32bit integer
      }
      return colors[Math.abs(hash) % colors.length]
    },
  },
}
</script>

<style scoped>
.chat-window {
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
}
</style>