<template>
  <layout-text>
    <template #header>
      <v-card flat>
        <v-card-title class="d-flex align-center">
          <span class="text-h5">Relatório de Anotadores</span>
          <v-spacer></v-spacer>
          <v-btn color="primary" :loading="loading" @click="generateReport">
            Gerar Relatório
          </v-btn>
        </v-card-title>
      </v-card>
    </template>

    <template #content>
      <v-card flat>
        <!-- Filtro de Anotadores e Labels -->
        <v-row>
          <v-col cols="12" md="6">
            <v-autocomplete
              v-model="selectedAnnotators"
              :items="annotatorsData"
              item-text="name"
              item-value="name"
              label="Anotadores"
              multiple
              chips
              :loading="loading"
              @change="filterAnnotators"
            ></v-autocomplete>
          </v-col>
          <v-col cols="12" md="6">
            <v-autocomplete
              v-model="selectedLabels"
              :items="availableLabels"
              label="Filtrar por Labels"
              multiple
              chips
              @change="filterAnnotators"
            ></v-autocomplete>
          </v-col>
        </v-row>

        <!-- Perspective Filters -->
        <v-row class="mt-2">
          <v-col cols="12" md="8" lg="6" class="ml-auto">
            <v-expansion-panels>
              <v-expansion-panel class="filter-panel">
                <v-expansion-panel-header class="filter-header">
                  <div class="d-flex align-center">
                    <v-icon left color="primary" class="mr-2">
                      mdi-filter-variant
                    </v-icon>
                    <span class="text-subtitle-2 font-weight-medium">
                      Filtros de Perspectiva
                    </span>
                  </div>
                  <template #actions>
                    <v-btn
                      v-if="hasActiveFilters"
                      small
                      text
                      color="error"
                      class="mr-2 clear-filters-btn"
                      @click.stop="clearFilters"
                    >
                      <v-icon small left>mdi-close</v-icon>
                      Limpar Filtros
                    </v-btn>
                    <v-icon color="primary" small>
                      {{
                        showFilters
                          ? 'mdi-chevron-up'
                          : 'mdi-chevron-down'
                      }}
                    </v-icon>
                  </template>
                </v-expansion-panel-header>
                <v-expansion-panel-content class="filter-content">
                  <v-row>
                    <v-col
                      v-for="(group, groupIndex) in perspectiveGroups"
                      :key="groupIndex"
                      cols="12"
                      md="6"
                    >
                      <v-card flat class="perspective-filter-card">
                        <v-card-title class="py-2">
                          <v-icon left color="primary" class="mr-2">
                            mdi-account-group
                          </v-icon>
                          <span class="text-subtitle-1 font-weight-medium">
                            {{ group.name }}
                          </span>
                        </v-card-title>
                        <v-divider class="mx-4"></v-divider>
                        <v-card-text class="py-2">
                          <div
                            v-for="question in group.questions"
                            :key="question.id"
                            class="mb-4"
                          >
                            <div class="d-flex align-center mb-1">
                              <v-icon
                                small
                                color="primary"
                                class="mr-2"
                              >
                                mdi-help-circle
                              </v-icon>
                              <div class="text-subtitle-2 font-weight-medium">
                                {{ question.question }}
                              </div>
                            </div>

                            <!-- String/Int Options -->
                            <v-select
                              v-if="question.data_type === 'string' || question.data_type === 'int'"
                              v-model="selectedAnswers[question.id]"
                              :items="question.options"
                              :label="'Selecionar ' + question.question"
                              multiple
                              chips
                              deletable-chips
                              clearable
                              outlined
                              dense
                              class="mt-1"
                              @change="applyFilters"
                            >
                              <template #selection="{ item, index }">
                                <v-chip
                                  v-if="index < 2"
                                  color="primary"
                                  outlined
                                  x-small
                                  class="mr-1"
                                >
                                  {{ item }}
                                </v-chip>
                                <span
                                  v-else-if="index === 2"
                                  class="grey--text text-caption pl-2"
                                >
                                  (+{{ selectedAnswers[question.id].length - 2 }} outros)
                                </span>
                              </template>
                            </v-select>

                            <!-- Boolean Options -->
                            <v-radio-group
                              v-else-if="question.data_type === 'boolean'"
                              v-model="selectedAnswers[question.id]"
                              row
                              dense
                              class="mt-1"
                              @change="applyFilters"
                            >
                              <v-radio
                                :value="true"
                                color="primary"
                                class="mr-4"
                              >
                                <template #label>
                                  <div class="d-flex align-center">
                                    <v-icon
                                      small
                                      color="success"
                                      class="mr-1"
                                    >
                                      mdi-check-circle
                                    </v-icon>
                                    <span class="text-caption">Sim</span>
                                  </div>
                                </template>
                              </v-radio>
                              <v-radio
                                :value="false"
                                color="primary"
                              >
                                <template #label>
                                  <div class="d-flex align-center">
                                    <v-icon
                                      small
                                      color="error"
                                      class="mr-1"
                                    >
                                      mdi-close-circle
                                    </v-icon>
                                    <span class="text-caption">Não</span>
                                  </div>
                                </template>
                              </v-radio>
                            </v-radio-group>
                          </div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                  </v-row>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-col>
        </v-row>

        <!-- Tabela de Anotadores -->
        <v-data-table
          :headers="headers"
          :items="filteredAnnotatorsData"
          :loading="loading"
          class="elevation-1"
        >
          <template #[`item.name`]="{ item }">
            <span>{{ item.name }}</span>
          </template>

          <template #[`item.labels`]="{ item }">
            <span>{{ (item.labels || []).join(', ') }}</span>
          </template>

          <template #[`item.annotations`]="{ item }">
            <span>{{ item.annotations.join(', ') }}</span>
          </template>
        </v-data-table>
      </v-card>
    </template>
  </layout-text>
</template>

<script>
import LayoutText from '@/components/tasks/layout/LayoutText.vue'
import { usePerspectiveApplicationService } from '@/services/application/perspective/perspectiveApplicationService'

export default {
  name: 'Anotadores',
  components: {
    LayoutText
  },
  layout: 'project',
  data() {
    return {
      loading: false,
      headers: [
        { text: 'Nome do Anotador', value: 'name', sortable: true },
        { text: 'Labels', value: 'labels', sortable: true },
        { text: 'Anotações', value: 'annotations', sortable: true }
      ],
      annotatorsData: [],
      filteredAnnotatorsData: [],
      selectedAnnotators: [],
      availableLabels: [],
      selectedLabels: [],
      perspectiveGroups: [],
      selectedAnswers: {}
    };
  },

  computed: {
    // Retorna true quando ao menos um filtro de perspectiva está selecionado
    hasActiveFilters() {
      return Object.values(this.selectedAnswers).some(value => {
        if (Array.isArray(value)) {
          return value.length > 0;
        }
        return value !== null && value !== undefined;
      });
    }
  },

  async mounted() {
    await this.fetchAnnotators();
    await this.fetchLabels();
    await this.fetchPerspectiveGroups();
  },

  methods: {
    filterAnnotators() {
      let data = this.annotatorsData;
      if (this.selectedAnnotators.length > 0) {
        data = data.filter(annotator =>
          this.selectedAnnotators.includes(annotator.name)
        );
      }
      if (this.selectedLabels.length > 0) {
        data = data.filter(annotator =>
          this.selectedLabels.some(label => (annotator.labels || []).includes(label))
        );
      }
      // Caso deseje filtrar também pelas perspectivas, implemente aqui

      this.filteredAnnotatorsData = data;
      console.log("Anotadores filtrados:", this.filteredAnnotatorsData);
    },

    async fetchAnnotators() {
      this.loading = true;
      try {
        const projectId = this.$route.params.id;
        console.log("ID do projeto atual:", projectId);
        const response = await this.$services.project.getMembers(projectId);
        console.log("Membros recebidos:", response);
        this.annotatorsData = response.map(member => ({
          name: member.username,
          annotations: member.annotations || [],
          datasets: member.datasets || [],
          labels: [] // Inicialmente vazio
        }));
        this.filteredAnnotatorsData = this.annotatorsData;
      } catch (error) {
        console.error('Erro ao buscar membros do projeto:', error);
      } finally {
        this.loading = false;
      }
    },

    async fetchLabels() {
      try {
        const projectId = this.$route.params.id;
        const labelsResponse = await this.$services.label.list(projectId);
        console.log("Labels do projeto:", labelsResponse.categories);
        this.annotatorsData = this.annotatorsData.map(annotator => {
          const labelsByAnnotator = labelsResponse.categories.filter(
            label => label.user === annotator.name
          );
          return {
            ...annotator,
            labels: labelsByAnnotator.map(label => label.label)
          };
        });
        console.log("Anotadores com labels:", this.annotatorsData);
        this.filteredAnnotatorsData = this.annotatorsData;
        this.availableLabels = [
          ...new Set(labelsResponse.categories.map(label => label.label))
        ];
        console.log("Available Labels:", this.availableLabels);
      } catch (error) {
        console.error("Erro ao buscar labels:", error);
      }
    },

    async fetchPerspectiveGroups() {
      try {
        const service = usePerspectiveApplicationService();
        const response = await service.listPerspectiveGroups(this.$route.params.id);
        this.perspectiveGroups = response.results || [];
        console.log("Grupos de perspectiva encontrados:", this.perspectiveGroups);
      } catch (err) {
        console.error('Error fetching perspective groups:', err);
        this.$store.dispatch('notification/open', {
          message: 'Erro ao carregar grupos de perspectiva.',
          type: 'error'
        });
      }
    },

    applyFilters() {
      this.filterAnnotators();
    },

    // Método para limpar as perspectivas selecionadas
    clearFilters() {
      console.log('Limpando filtros de perspectiva...');
      this.selectedAnswers = {};
      this.$nextTick(() => {
        this.applyFilters();
      });
    },

    generateReport() {
      alert('Relatório gerado!');
    }
  }
};
</script>