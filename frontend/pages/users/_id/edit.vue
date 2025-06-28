<template>
  <div class="form-container">
    <v-card class="user-form">
      <v-card-title>
        <span class="text-h5">Edit User</span>
        <v-spacer></v-spacer>
      </v-card-title>

      <!-- Error message -->
      <transition name="fade">
        <div v-if="errorMessage" class="error-message">
          <v-icon small class="mr-2" color="error">mdi-alert-circle</v-icon>
          {{ errorMessage }}
        </div>
      </transition>

      <!-- Success message -->
      <transition name="fade">
        <div v-if="showSuccess" class="success-message">
          <v-icon small class="mr-2" color="success">mdi-check-circle</v-icon>
          User updated successfully!
        </div>
      </transition>

      <v-card-text>
        <v-form v-model="valid" ref="form">
          <v-text-field
            v-model="userData.username"
            :rules="userNameRules('Username is required')"
            label="Username"
            name="username"
            :prepend-icon="mdiAccount"
            type="text"
            dense
          />
          <v-text-field
            v-model="userData.first_name"
            label="First Name"
            name="first_name"
            :prepend-icon="mdiAccount"
            dense
          />
          <v-text-field
            v-model="userData.last_name"
            label="Last Name"
            name="last_name"
            :prepend-icon="mdiAccount"
            dense
          />
          <v-text-field
            v-model="userData.email"
            :rules="emailRules"
            label="Email"
            name="email"
            :prepend-icon="mdiEmail"
            type="email"
            dense
          />
          <!-- Perfil dropdown -->
          <v-select
            v-model="selectedGroupId"
            :items="groupsOptions"
            item-text="name"
            item-value="id"
            label="Perfil (opcional)"
            dense
          />
          <v-text-field
            v-model="userData.password1"
            :rules="optionalPasswordRules"
            label="Password"
            name="password1"
            :prepend-icon="mdiLock"
            type="password"
            dense
          />
          <v-text-field
            v-model="userData.password2"
            :rules="[confirmPasswordRequiredRule, passwordMatchRule]"
            label="Confirm Password"
            name="password2"
            :prepend-icon="mdiLock"
            type="password"
            dense
          />
          <!-- Superuser toggle -->
          <v-switch
            v-model="userData.is_superuser"
            color="primary"
            label="Make user a superuser (administrator)"
            class="mt-4"
            dense
          />
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          class="text-capitalize mr-3"
          outlined
          color="error"
          @click="goBack"
        >
          {{ $t('generic.cancel') || 'Cancel' }}
        </v-btn>
        <v-btn
          :disabled="!canSave"
          color="primary"
          class="text-capitalize"
          @click="updateUser"
        >
          {{ $t('generic.save') || 'Save' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiAccount, mdiLock, mdiEmail, mdiCheckCircle, mdiAlertCircle } from '@mdi/js'
import { userNameRules, passwordRules } from '@/rules/index'
import { APIUserRepository } from '@/repositories/user/apiUserRepository'
import userService from '~/services/userService'

export default Vue.extend({
  layout: 'projects',
  middleware: ['check-auth', 'auth'],

  data() {
    return {
      valid: false,
      showSuccess: false,
      errorMessage: '',
      userData: {
        id: null,
        username: '',
        first_name: '',
        last_name: '',
        email: '',
        password1: '',
        password2: '',
        is_superuser: false,
        groups: [] as string[]
      },
      userNameRules,
      passwordRules,
      mdiAccount,
      mdiLock,
      mdiEmail,
      mdiCheckCircle,
      mdiAlertCircle,
      emailRules: [
        (v: string) => !!v || 'Email is required',
        (v: string) => /.+@.+\..+/.test(v) || 'Email must be valid'
      ],
      optionalPasswordRules: [
        (v: string) => !v || (v.length <= 30) || 'Password must be less than 30 chars'
      ],
      groupsOptions: [] as { id: number; name: string }[],
      selectedGroupId: null as number | null,
    }
  },

  computed: {
    canSave(): boolean {
      if (!this.valid) return false
      const p1 = this.userData.password1
      const p2 = this.userData.password2
      if (!p1) return true // no password change, other fields valid
      return !!p2 && p1 === p2 // only enable if both passwords filled and match
    },
    confirmPasswordRequiredRule() {
      return (v: string) =>
        !this.userData.password1 || !!v || 'Confirm password is required'
    },
    passwordMatchRule() {
      return () =>
        this.userData.password1 === this.userData.password2 ||
        'Passwords must match'
    }
  },

  async fetch() {
    // Load existing user data
    const id = this.$route.params.id
    try {
      const repo = new APIUserRepository()
      const user: any = await repo.findById(id)
      this.userData.id = user.id
      this.userData.username = user.username
      this.userData.first_name = user.first_name || ''
      this.userData.last_name = user.last_name || ''
      this.userData.email = user.email
      this.userData.is_superuser = user.is_superuser || false
      this.userData.groups = user.groups || []

      // buscar grupos
      const res = await this.$axios.get('/v1/groups/')
      this.groupsOptions = res.data
      if (this.userData.groups.length) {
        const current = this.groupsOptions.find(g => this.userData.groups.includes(g.name))
        if (current) this.selectedGroupId = current.id
      }
    } catch (error) {
      console.error('Error fetching user:', error)
      this.errorMessage = 'Failed to load user information.'
    }
  },

  methods: {
    async updateUser() {
      if (!this.valid) return

      try {
        this.errorMessage = ''
        const payload: any = {
          username: this.userData.username,
          first_name: this.userData.first_name,
          last_name: this.userData.last_name,
          email: this.userData.email,
          is_superuser: this.userData.is_superuser
        }
        if (this.userData.password1) {
          payload.password = this.userData.password1
        }
        if (this.selectedGroupId) {
          payload.groups_ids = [this.selectedGroupId]
        }
        await userService.updateUser(this.userData.id, payload)
        this.showSuccess = true
        // Após sucesso, volta à lista de utilizadores
        setTimeout(() => this.$router.push('/users'), 1000)
      } catch (error) {
        console.error('Error updating user:', error)
        this.errorMessage = 'Database unavailable at the moment, please try again later.'
      }
    },
    goBack() {
      this.$router.push('/users')
    }
  }
})
</script>

<style scoped>
.form-container {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  padding: 16px;
}

.user-form {
  max-width: 1500px;
  width: 100%;
  margin-left: 0;
}

.success-message {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000;
  background-color: #e6f4ea;
  color: #2e7d32;
  padding: 12px 24px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  font-weight: 500;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  pointer-events: none;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.error-message {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000;
  background-color: #fdecea;
  color: #b71c1c;
  padding: 12px 24px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  font-weight: 500;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  pointer-events: none;
}
</style> 