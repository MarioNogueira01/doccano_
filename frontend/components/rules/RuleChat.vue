<template>
  <div>
    <v-card outlined class="pa-2 mb-4">
      <v-card-title class="subtitle-2 grey--text text--darken-1">
        Discussão da Regra
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
      
      <!-- Read-only mode alert -->
      <v-alert v-if="readOnly" type="info" dense text>
        Chat em modo de leitura.
      </v-alert>
      
      <!-- Message input area - only show if not read-only -->
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

    <!-- Snackbar moved outside the card to ensure visibility -->
    <v-snackbar
      v-model="snackbar"
      :color="snackbarColor"
      timeout="5000"
      top
      :value="snackbar"
    >
      {{ snackbarText }}
      <template #action="{ attrs }">
        <v-btn
          text
          v-bind="attrs"
          @click="snackbar = false"
        >
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
export default {
  name: 'RuleChat',
  props: {
    projectId: { type: [String, Number], required: true },
    sessionId: { type: [String, Number], required: true },
    questionIndex: { type: Number, required: true },
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
        const res = await this.$services.ruleDiscussion.list(
          this.projectId,
          this.sessionId,
          this.questionIndex
        )
        this.messages = res.messages || res
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
      if (!this.newMessage.trim()) return
      
      const messageText = this.newMessage.trim()
      this.newMessage = ''
      this.loading = true
      
      try {
        const newMsg = await this.$services.ruleDiscussion.create(
          this.projectId,
          this.sessionId,
          this.questionIndex,
          messageText
        )
        
        // Add the new message to the list
        this.messages.push(newMsg)
        
        // Scroll to bottom to show the new message
        this.$nextTick(() => {
          this.scrollToBottom()
        })
        
        this.showSuccess('Mensagem enviada com sucesso!')
      } catch (e) {
        console.error('Erro ao enviar mensagem', e)
        console.error('Error response:', e.response)
        console.error('Error status:', e.response?.status)
        
        // Handle database unavailable error (503)
        let errorMessage = 'Erro ao enviar mensagem. Por favor, tente novamente.'
        
        if (!e.response || (e.response.status && e.response.status >= 500)) {
          errorMessage = 'Database unavailable at the moment, please try again later.'
        }
        
        console.log('About to show error:', errorMessage)
        
        // Emit error to parent component for display at page level
        this.$emit('error', errorMessage)
        
        // Also try to show locally
        this.showError(errorMessage)
        
        // Restore the message text if sending failed
        this.newMessage = messageText
      } finally {
        this.loading = false
      }
    },
    showError(message) {
      console.log('showError called with:', message)
      this.snackbarText = message
      this.snackbarColor = 'error'
      this.snackbar = true
      console.log('snackbar state:', this.snackbar, this.snackbarText, this.snackbarColor)
    },
    showSuccess(message) {
      console.log('showSuccess called with:', message)
      this.snackbarText = message
      this.snackbarColor = 'success'
      this.snackbar = true
      console.log('snackbar state:', this.snackbar, this.snackbarText, this.snackbarColor)
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
      // Define a palette of distinct colors
      const colors = [
        '#FF0000', // Red
        '#00A0FF', // Blue
        '#00FF00', // Green
        '#FF00FF', // Magenta
        '#FFA500', // Orange
        '#9400D3', // Purple
        '#008080', // Teal
        '#FF4500', // Orange-Red
        '#FFD700', // Gold
        '#4B0082', // Indigo
        '#800000', // Maroon
        '#00FFFF', // Cyan
        '#8B4513', // Brown
        '#000000', // Black
        '#708090'  // Slate Gray
      ]
      
      // Create a hash from the username
      let hash = 0
      for (let i = 0; i < username.length; i++) {
        hash = ((hash << 5) - hash) + username.charCodeAt(i)
        hash = hash & hash // Convert to 32bit integer
      }
      
      // Use the hash to pick a color from our palette
      const index = Math.abs(hash) % colors.length
      return colors[index]
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