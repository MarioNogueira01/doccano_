<template>
  <v-card>
    <v-card-title>
      <span class="text-h5">Edit User</span>
    </v-card-title>

    <v-card-text>
      <v-form v-if="user" v-model="valid" ref="form">
        <v-text-field
          v-model="formData.username"
          label="Username"
          :rules="usernameRules"
          required
        />
        <v-text-field
          v-model="formData.first_name"
          label="First Name"
        />
        <v-text-field
          v-model="formData.last_name"
          label="Last Name"
        />
        <v-text-field
          v-model="formData.email"
          label="Email"
          type="email"
          :rules="emailRules"
          required
        />
        <v-text-field
          v-model="formData.password1"
          label="Password"
          type="password"
          :rules="passwordRules"
          required
        />
        <v-text-field
          v-model="formData.password2"
          label="Confirm Password"
          type="password"
          :rules="[...passwordRules, passwordMatchRule]"
          required
        />
      </v-form>
    </v-card-text>

    <v-card-actions>
      <v-btn color="primary" text @click="onCancel">Cancelar</v-btn>
      <v-btn color="primary" :disabled="!valid" @click="onSave">Salvar</v-btn>
    </v-card-actions>

    <!-- Snackbar de erro -->
    <v-snackbar
      v-model="dbErrorVisible"
      :timeout="4000"
      color="error"
      top
    >
      {{ dbErrorMessage }}
    </v-snackbar>
  </v-card>
</template>

<script>
import userService from '~/services/userService'

export default {
  name: 'UserEditForm',
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      formData: {
        id: null,
        username: '',
        first_name: '',
        last_name: '',
        email: '',
        password1: '',
        password2: ''
      },
      valid: false,
      usernameRules: [(v) => !!v || 'Campo obrigatório'],
      emailRules: [
        (v) => !!v || 'Campo obrigatório',
        (v) => /.+@.+\..+/.test(v) || 'Email inválido'
      ],
      passwordRules: [(v) => !!v || 'Campo obrigatório'],
      // Snackbar de erro de base de dados
      dbErrorVisible: false,
      dbErrorMessage: ''
    }
  },
  computed: {
    passwordMatchRule() {
      return () =>
        this.formData.password1 === this.formData.password2 ||
        'Passwords must match'
    }
  },
  watch: {
    'user.id': {
      immediate: true,
      handler(newId) {
        // Se "selectedUser" mudar de ID, atualiza formData
        this.formData.id = newId
        this.formData.username = this.user.username
        this.formData.first_name = this.user.first_name
        this.formData.last_name = this.user.last_name
        this.formData.email = this.user.email
        this.formData.password1 = ''
        this.formData.password2 = ''
      }
    }
  },
  methods: {
    onCancel() {
      this.$emit('cancel')
    },
    async onSave() {
      if (!this.$refs.form.validate()) return;

      try {
        console.log('Atualizando utilizador ID:', this.formData.id)

        const payload = {
          username: this.formData.username,
          first_name: this.formData.first_name,
          last_name: this.formData.last_name,
          email: this.formData.email
        }
        if (this.formData.password1) {
          payload.password = this.formData.password1
        }

        await userService.updateUser(this.formData.id, payload)

        // Limpar o campo da senha
        this.formData.password1 = ''
        this.formData.password2 = ''

        // Emite para o pai que salvou
        this.$emit('saved')
      } catch (error) {
        console.error('Erro ao atualizar usuário:', error)
        // Se não houver resposta do servidor ou erro 5xx, assume indisponibilidade da base de dados
        if (!error.response || (error.response.status && error.response.status >= 500)) {
          this.dbErrorMessage = 'Database unavailable at the moment, please try again later.'
        } else if (error.response.status === 400 && error.response.data?.username) {
          // Erro de validação: nome de utilizador duplicado
          this.dbErrorMessage = 'Este nome de utilizador ja esta a ser usado.'
        } else {
          // Demais erros
          this.dbErrorMessage = error.response.data?.detail || 'Ocorreu um erro ao atualizar o usuário.'
        }
        this.dbErrorVisible = true
      }
    }
  }
}
</script>
