<template>
  <v-container>
    <h1 class="text-h4 mb-4">History of Annotations</h1>

    <!-- Tabs for Annotations and Annotators -->
    <v-tabs v-model="selectedTab" class="mb-4">
      <v-tab href="#tab-annotations">
        Annotations
      </v-tab>
      <v-tab href="#tab-annotators">
        Annotators
      </v-tab>
    </v-tabs>

    <v-card>
      <v-card-title>
        <!-- Report Type dropdown -->
        <v-select
          v-model="selectedReportType"
          :items="reportTypes"
          label="Report Type"
          outlined
          dense
          class="mb-2"
        ></v-select>
        <v-spacer></v-spacer>
        <v-btn color="primary" :loading="loading" :disabled="loading"
         type="button" @click="generateReport">
          <v-icon left>mdi-file-document-outline</v-icon>
          Generate Report
        </v-btn>
        <v-btn color="primary" outlined :disabled="!downloadReady" type="button"
         @click="showExportDialog = true">
          <v-icon left>mdi-download</v-icon>
          Export Report
        </v-btn>
      </v-card-title>

      <v-card-text>
        <!-- Content for Annotations Tab -->
        <v-tabs-items v-model="selectedTab">
          <v-tab-item value="tab-annotations">
            <v-toolbar flat dense class="mb-4">
              <v-spacer></v-spacer>
              <v-select
                v-model="selectedDatasetName"
                :items="datasetNames"
                label="Dataset"
                outlined
                dense
                class="mb-2"
                @change="handleDatasetChange"
              ></v-select>
              <v-select
                v-model="selectedAnnotationStatus"
                :items="annotationStatuses"
                label="Annotation Status"
                outlined
                dense
                class="mb-2"
                @change="handleAnnotationStatusChange"
              ></v-select>
              <v-btn text @click="clearFilters">
                CLEAR FILTERS
              </v-btn>
            </v-toolbar>
            <v-data-table
              :headers="headers"
              :items="filteredAnnotations"
              :loading="loading"
              class="elevation-1 mb-4"
            ></v-data-table>

            <!-- Perspectives Table -->
            <v-divider class="my-6"></v-divider>
            
            <v-card-title class="px-0">
              <h2 class="text-h5">Perspectives</h2>
              <v-spacer></v-spacer>
              <v-btn color="primary" class="mr-2" :loading="loadingPerspectives"
               :disabled="loadingPerspectives" @click="generatePerspectivesReport">
                <v-icon left>mdi-file-document-outline</v-icon>
                Generate Perspectives
              </v-btn>
              <v-btn color="primary" outlined :disabled="
              !perspectivesDownloadReady" @click="showPerspectivesExportDialog = true">
                <v-icon left>mdi-download</v-icon>
                Export Perspectives
              </v-btn>
            </v-card-title>

            <v-row class="mb-2" align="center">
              <v-col cols="12" sm="4" md="3">
                <v-select
                  v-model="selectedPerspectiveAnswerType"
                  :items="perspectiveAnswerTypes"
                  label="Filter by Answer Type"
                  dense
                  outlined
                ></v-select>
              </v-col>
            </v-row>
            <v-data-table
              :headers="perspectiveHeaders"
              :items="filteredPerspectives"
              :loading="loadingPerspectives"
              class="elevation-1"
            ></v-data-table>

            <!-- Discrepancies Table -->
            <v-divider class="my-6"></v-divider>

            <v-card-title class="px-0">
              <h2 class="text-h5">Discrepancies</h2>
              <v-spacer></v-spacer>
              <v-btn
                color="primary"
                class="mr-2"
                :loading="loadingDiscrepancies"
                :disabled="loadingDiscrepancies"
                @click="generateDiscrepancyReport"
              >
                <v-icon left>mdi-file-document-outline</v-icon>
                Generate Discrepancies
              </v-btn>
              <v-btn
                color="primary"
                outlined
                :disabled="!discrepancyDownloadReady"
                @click="showDiscrepanciesExportDialog = true"
              >
                <v-icon left>mdi-download</v-icon>
                Export Discrepancies
              </v-btn>
            </v-card-title>
            
            <v-data-table
              :headers="discrepancyHeaders"
              :items="discrepancies.map(d => ({ ...d, perspective_answers: undefined }))"
              :loading="loadingDiscrepancies"
              class="elevation-1"
            ></v-data-table>
          </v-tab-item>

          <!-- Content for Annotators Tab -->
          <v-tab-item value="tab-annotators">
            <p>Content for Annotation History (Annotators view)</p>
          </v-tab-item>
        </v-tabs-items>
      </v-card-text>
    </v-card>

    <!-- Export Format Dialog -->
    <v-dialog v-model="showExportDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h5">
          <v-icon left color="primary">mdi-download</v-icon>
          Choose Export Format
        </v-card-title>
        <v-card-text>
          <v-radio-group v-model="selectedExportFormat" class="mt-4">
            <v-radio label="PDF" value="pdf">
              <template #label>
                <div class="d-flex align-center">
                  <v-icon left color="red" class="mr-2">mdi-file-pdf-box</v-icon>
                  PDF Format
                </div>
              </template>
            </v-radio>
            <v-radio label="CSV" value="csv">
              <template #label>
                <div class="d-flex align-center">
                  <v-icon left color="green" class="mr-2">mdi-file-excel</v-icon>
                  CSV Format
                </div>
              </template>
            </v-radio>
          </v-radio-group>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showExportDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="handleExport">
            <v-icon left>mdi-download</v-icon>
            Export
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Perspectives Export Format Dialog -->
    <v-dialog v-model="showPerspectivesExportDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h5">
          <v-icon left color="primary">mdi-download</v-icon>
          Choose Export Format
        </v-card-title>
        <v-card-text>
          <v-radio-group v-model="selectedPerspectivesExportFormat" class="mt-4">
            <v-radio label="PDF" value="pdf">
              <template #label>
                <div class="d-flex align-center">
                  <v-icon left color="red" class="mr-2">mdi-file-pdf-box</v-icon>
                  PDF Format
                </div>
              </template>
            </v-radio>
            <v-radio label="CSV" value="csv">
              <template #label>
                <div class="d-flex align-center">
                  <v-icon left color="green" class="mr-2">mdi-file-excel</v-icon>
                  CSV Format
                </div>
              </template>
            </v-radio>
          </v-radio-group>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showPerspectivesExportDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="handlePerspectivesExport">
            <v-icon left>mdi-download</v-icon>
            Export
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Discrepancies Export Format Dialog -->
    <v-dialog v-model="showDiscrepanciesExportDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h5">
          <v-icon left color="primary">mdi-download</v-icon>
          Choose Export Format
        </v-card-title>
        <v-card-text>
          <v-radio-group v-model="selectedDiscrepanciesExportFormat" class="mt-4">
            <v-radio label="PDF" value="pdf">
              <template #label>
                <div class="d-flex align-center">
                  <v-icon left color="red" class="mr-2">mdi-file-pdf-box</v-icon>
                  PDF Format
                </div>
              </template>
            </v-radio>
            <v-radio label="CSV" value="csv">
              <template #label>
                <div class="d-flex align-center">
                  <v-icon left color="green" class="mr-2">mdi-file-excel</v-icon>
                  CSV Format
                </div>
              </template>
            </v-radio>
          </v-radio-group>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showDiscrepanciesExportDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="handleDiscrepanciesExport">
            <v-icon left>mdi-download</v-icon>
            Export
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { mdiMagnify } from '@mdi/js'

export default {
  name: 'AnnotationHistory',
  layout: 'project',

  validate({ params }) {
    return /^\d+$/.test(params.id)
  },

  data() {
    return {
      selectedTab: 'tab-annotations', // Default selected tab
      datasetNames: [], // Dynamically loaded dataset names
      selectedDatasetName: null,
      annotationStatuses: ['All', 'Finished', 'In progress', 'Not started'], // Annotation statuses
      selectedAnnotationStatus: null, // Default annotation status to null for empty filter
      headers: [
        { text: 'Annotator', value: 'annotator' },
        { text: 'Label', value: 'label' },
        { text: 'Date', value: 'date' },
        { text: 'Example Text', value: 'example_text' },
        { text: 'Number of Annotations', value: 'numberOfAnnotations' },
      ],
      perspectiveHeaders: [
        { text: 'Perspective Question', value: 'question' },
        { text: 'Perspective Answer', value: 'answer' },
        { text: 'Answered By', value: 'answered_by' },
        { text: 'Answer Date', value: 'answer_date' },
      ],
      discrepancyHeaders: [
        { text: 'Example ID', value: 'example_id' },
        { text: 'Text', value: 'text' },
        { text: 'Is Discrepancy', value: 'is_discrepancy' },
        { text: 'Max. Percentage', value: 'max_percentage' }
      ],
      annotations: [], // Initialize as empty array
      perspectives: [], // Initialize perspectives array
      discrepancies: [], // Initialize discrepancies array
      loading: false,
      loadingPerspectives: false,
      loadingDiscrepancies: false,
      taskId: null,
      perspectivesTaskId: null,
      discrepancyTaskId: null,
      polling: null,
      perspectivesPolling: null,
      discrepancyPolling: null,
      downloadReady: false,
      perspectivesDownloadReady: false,
      discrepancyDownloadReady: false,
      mdiMagnify,
      showExportDialog: false,
      selectedExportFormat: 'pdf',
      showPerspectivesExportDialog: false,
      selectedPerspectivesExportFormat: 'pdf',
      selectedPerspectiveAnswerType: 'All',
      perspectiveAnswerTypes: ['All', 'Yes/No', 'Number', 'Text'],
      selectedReportType: null,
      reportTypes: ['Annotation History'],
      showDiscrepanciesExportDialog: false,
      selectedDiscrepanciesExportFormat: 'pdf',
    };
  },
  computed: {
    projectId() {
      return this.$route.params.id
    },
    filteredAnnotations() {
      if (!this.selectedAnnotationStatus || this.selectedAnnotationStatus === 'All') {
        return this.annotations;
      }
      if (this.selectedAnnotationStatus === 'Finished') {
        return this.annotations.filter(a => {
          // Considera finished se tiver um valor em 'date' e não estiver "in progress"
          return a.date && (!a.status || a.status === 'Finished');
        });
      }
      if (this.selectedAnnotationStatus === 'In progress') {
        return this.annotations.filter(a => {
          // Tem label (ou seja, alguém já começou), mas ainda não tem data de conclusão
          return a.label && (!a.date || a.date === 'N/A');
        });
      }
      if (this.selectedAnnotationStatus === 'Not started') {
        return this.annotations.filter(a => {
          // Considera not started se não tiver data nem label
          return (!a.date || a.date === 'N/A') && (!a.label || a.label === 'N/A');
        });
      }
      return this.annotations;
    },
    filteredPerspectives() {
      if (this.selectedPerspectiveAnswerType === 'All') return this.perspectives;
      if (this.selectedPerspectiveAnswerType === 'Yes/No') {
        return this.perspectives.filter(p => {
          const val = (p.answer || '').toLowerCase();
          return val === 'yes' || val === 'no';
        });
      }
      if (this.selectedPerspectiveAnswerType === 'Number') {
        return this.perspectives.filter(p => !isNaN(Number(p.answer)) && p.answer !== '' && p.answer !== null);
      }
      if (this.selectedPerspectiveAnswerType === 'Text') {
        return this.perspectives.filter(p => {
          const val = (p.answer || '').toLowerCase();
          return val !== 'yes' && val !== 'no' && isNaN(Number(p.answer));
        });
      }
      return this.perspectives;
    }
  },
  created() {
    this.fetchDatasetNames();
    // this.fetchData(); // No longer calling fetchData directly on created
  },
  beforeDestroy() {
    clearInterval(this.polling);
    clearInterval(this.perspectivesPolling);
    clearInterval(this.discrepancyPolling);
  },
  methods: {
    async fetchDatasetNames() {
      try {
        const response = await this.$repositories.example.fetchDatasetNames(this.projectId);
        this.datasetNames = response.datasetNames;
      } catch (error) {
        console.error("Error fetching dataset names:", error);
        this.$toasted.error('Error loading dataset names');
      }
    },

    async generateReport() {
      this.loading = true;
      this.downloadReady = false;
      this.annotations = []; // Clear previous annotations
      try {
        this.taskId = await this.$repositories.annotationHistory.prepare(
          this.projectId,
          this.selectedDatasetName,
          this.selectedAnnotationStatus
        );
        this.pollTaskStatus();
      } catch (error) {
        if (!error.response || (error.response && [500, 502, 503, 504].includes(
          error.response.status))) {
          this.$toasted.error('The server/database is unavailable. Please check if the backend is running.');
        } else {
          this.$toasted.error('Error generating report');
        }
        this.loading = false;
      }
    },

    async generatePerspectivesReport() {
      this.loadingPerspectives = true;
      this.perspectivesDownloadReady = false;
      this.perspectives = []; // Clear previous perspectives
      try {
        this.perspectivesTaskId = await this.$repositories.annotationHistory.prepare(
          this.projectId,
          this.selectedDatasetName,
          this.selectedAnnotationStatus
        );
        this.pollPerspectivesTaskStatus();
      } catch (error) {
        if (!error.response || (error.response && [500, 502, 503, 504].includes(
          error.response.status))) {
          this.$toasted.error('The server/database is unavailable. Please check if the backend is running.');
        } else {
          this.$toasted.error('Error generating perspectives report');
        }
        this.loadingPerspectives = false;
      }
    },

    async generateDiscrepancyReport() {
      this.loadingDiscrepancies = true;
      this.discrepancyDownloadReady = false;
      this.discrepancies = []; // Clear previous discrepancies
      try {
        this.discrepancyTaskId = await this.$repositories.discrepancyHistory.prepare(
          this.projectId,
          this.selectedDatasetName
        );
        this.pollDiscrepancyTaskStatus();
      } catch (error) {
        if (!error.response || (error.response && [500, 502, 503, 504].includes(
          error.response.status))) {
          this.$toasted.error('The server/database is unavailable. Please check if the backend is running.');
        } else {
          this.$toasted.error('Error generating discrepancy report');
        }
        this.loadingDiscrepancies = false;
      }
    },

    pollTaskStatus() {
      if (this.polling) {
        clearInterval(this.polling);
        this.polling = null;
      }

      this.polling = setInterval(async () => {
        if (!this.taskId) {
          clearInterval(this.polling);
          this.polling = null;
          return;
        }

        try {
          const res = await this.$repositories.taskStatus.get(this.taskId);
          console.log("Task status response for annotations:", res);

          if (res && res.ready) {
            if (!res.error) { // Consider success if ready and no error
              clearInterval(this.polling);
              this.polling = null;
              this.loading = false;

              // Fetch the actual data for the table
              const data = await this.$repositories.annotationHistory.fetch(
                this.projectId,
                this.taskId
              );

              this.annotations = data.map(item => {
                let formattedDate = 'N/A';
                if (item.date && item.date !== 'N/A') {
                  try {
                    const date = new Date(item.date);
                    if (!isNaN(date.getTime())) {
                      formattedDate = date.toLocaleString();
                    }
                  } catch (e) {
                    console.warn('Invalid date format for annotation:', item.date);
                  }
                }
                
                return {
                  ...item,
                  date: formattedDate
                };
              });

              console.log("Fetched annotations:", this.annotations);
              this.downloadReady = true;
              this.$toasted.success('Annotations report generated successfully!');
            } else { // Consider failure if ready and has error
              clearInterval(this.polling);
              this.polling = null;
              this.loading = false;
              this.$toasted.error(`Error generating annotations report: ${res.error || 'Unknown error'}`);
            }
          }
        } catch (error) {
          console.error("Error polling task status:", error);
          this.$toasted.error('Error polling report status');
          clearInterval(this.polling);
          this.polling = null;
          this.loading = false;
        }
      }, 1000);
    },

    pollPerspectivesTaskStatus() {
      if (this.perspectivesPolling) {
        clearInterval(this.perspectivesPolling);
        this.perspectivesPolling = null;
      }

      this.perspectivesPolling = setInterval(async () => {
        if (!this.perspectivesTaskId) {
          clearInterval(this.perspectivesPolling);
          this.perspectivesPolling = null;
          return;
        }

        try {
          const res = await this.$repositories.taskStatus.get(this.perspectivesTaskId);
          console.log("Task status response for perspectives:", res);

          if (res && res.ready) {
            if (!res.error) { // Consider success if ready and no error
              clearInterval(this.perspectivesPolling);
              this.perspectivesPolling = null;
              this.loadingPerspectives = false;

              // Fetch the actual data for the table
              const data = await this.$repositories.annotationHistory.fetch(
                this.projectId,
                this.perspectivesTaskId
              );
              console.log("Raw data fetched for perspectives:", data);

              // Process only perspectives data
              const perspectivesData = data.reduce((acc, item, index) => {
                let currentPerspectives = [];
                console.log(`Processing item ${index}: item.perspectives type: ${typeof item.perspectives}, value:`, item.perspectives);

                // Ensure item.perspectives is a non-empty string before attempting JSON.parse
                if (typeof item.perspectives === 'string') {
                  if (item.perspectives.trim().length > 0) {
                    try {
                      // Log the string before parsing
                      console.log(`Attempting to parse JSON string for item ${index}:`, item.perspectives);
                      currentPerspectives = JSON.parse(item.perspectives);
                    } catch (e) {
                      console.error("Error parsing perspectives data (string):", e, item.perspectives);
                      currentPerspectives = [];
                    }
                  } else {
                    console.log(`Item ${index}.perspectives is an empty or whitespace-only string, setting to empty array.`);
                    currentPerspectives = [];
                  }
                } else if (Array.isArray(item.perspectives)) {
                  console.log(`Item ${index}.perspectives is already an array:`, item.perspectives);
                  currentPerspectives = item.perspectives;
                } else {
                  console.log(`Item ${index}.perspectives is neither a string nor an array (or is null/undefined). Setting to empty array.`, item.perspectives);
                  currentPerspectives = []; // Ensure it's an array if it's null/undefined/other
                }

                if (Array.isArray(currentPerspectives)) {
                  currentPerspectives.forEach(perspective => {
                    let formattedDate = 'N/A';
                    if (perspective.answer_date && perspective.answer_date !== 'N/A') {
                      try {
                        const date = new Date(perspective.answer_date);
                        if (!isNaN(date.getTime())) {
                          formattedDate = date.toLocaleString();
                        }
                      } catch (e) {
                        console.warn('Invalid date format:', perspective.answer_date);
                      }
                    }
                    
                    acc.push({
                      ...perspective,
                      answer_date: formattedDate
                    });
                  });
                }
                return acc;
              }, []);

              this.perspectives = perspectivesData;
              console.log("Fetched perspectives (after processing):", this.perspectives);
              this.perspectivesDownloadReady = true;
              this.$toasted.success('Perspectives report generated successfully!');
            } else { // Consider failure if ready and has error
              clearInterval(this.perspectivesPolling);
              this.perspectivesPolling = null;
              this.loadingPerspectives = false;
              this.$toasted.error(`Error generating perspectives report: ${res.error || 'Unknown error'}`);
            }
          }
        } catch (error) {
          console.error("Error polling perspectives task status:", error);
          this.$toasted.error('Error polling perspectives report status');
          clearInterval(this.perspectivesPolling);
          this.perspectivesPolling = null;
          this.loadingPerspectives = false;
        }
      }, 1000);
    },

    pollDiscrepancyTaskStatus() {
      if (this.discrepancyPolling) {
        clearInterval(this.discrepancyPolling);
        this.discrepancyPolling = null;
      }

      this.discrepancyPolling = setInterval(async () => {
        if (!this.discrepancyTaskId) {
          clearInterval(this.discrepancyPolling);
          this.discrepancyPolling = null;
          return;
        }

        try {
          const res = await this.$repositories.taskStatus.get(this.discrepancyTaskId);
          if (res && res.ready) {
            if (!res.error) {
              clearInterval(this.discrepancyPolling);
              this.discrepancyPolling = null;
              this.loadingDiscrepancies = false;

              const data = await this.$repositories.discrepancyHistory.fetch(
                this.projectId,
                this.discrepancyTaskId
              );
              this.discrepancies = data;
              this.discrepancyDownloadReady = true;
              this.$toasted.success('Discrepancy report generated successfully!');
            } else {
              clearInterval(this.discrepancyPolling);
              this.discrepancyPolling = null;
              this.loadingDiscrepancies = false;
              this.$toasted.error(`Error generating discrepancy report: ${res.error || 'Unknown error'}`);
            }
          }
        } catch (error) {
          console.error("Error polling discrepancy task status:", error);
          this.$toasted.error('Error polling discrepancy report status');
          clearInterval(this.discrepancyPolling);
          this.discrepancyPolling = null;
          this.loadingDiscrepancies = false;
        }
      }, 1000);
    },

    async downloadReport() {
      this.loading = true;
      try {
        const downloadTaskId = await this.$repositories.annotationHistory.prepare(
          this.projectId,
          this.selectedDatasetName,
          this.selectedAnnotationStatus
        );

        let downloadPolling = null;
        downloadPolling = setInterval(async () => {
          const res = await this.$repositories.taskStatus.get(downloadTaskId);
          console.log("Download task status response for annotations:", res);
          if (res && res.ready) {
            if (!res.error) { // Consider success if ready and no error
              clearInterval(downloadPolling);
              this.loading = false;
              this.$repositories.annotationHistory.downloadFile(this.projectId, downloadTaskId);
              this.$toasted.success('Annotations report downloaded successfully!');
            } else { // Consider failure if ready and has error
              clearInterval(downloadPolling);
              this.loading = false;
              this.$toasted.error(`Error downloading annotations report: ${res.error || 'Unknown error'}`);
            }
          }
        }, 1000);

      } catch (error) {
        console.error("Error initiating download:", error);
        this.$toasted.error('Error initiating annotations report download');
        this.loading = false;
      }
    },

    async downloadPerspectivesReport() {
      this.loadingPerspectives = true;
      try {
        const downloadTaskId = await this.$repositories.annotationHistory.prepare(
          this.projectId,
          this.selectedDatasetName,
          this.selectedAnnotationStatus
        );

        let downloadPolling = null;
        downloadPolling = setInterval(async () => {
          const res = await this.$repositories.taskStatus.get(downloadTaskId);
          console.log("Download task status response for perspectives:", res);
          if (res && res.ready) {
            if (!res.error) { // Consider success if ready and no error
              clearInterval(downloadPolling);
              this.loadingPerspectives = false;
              this.$repositories.annotationHistory.downloadFile(this.projectId, downloadTaskId);
              this.$toasted.success('Perspectives report downloaded successfully!');
            } else { // Consider failure if ready and has error
              clearInterval(downloadPolling);
              this.loadingPerspectives = false;
              this.$toasted.error(`Error downloading perspectives report: ${res.error || 'Unknown error'}`);
            }
          }
        }, 1000);

      } catch (error) {
        console.error("Error initiating perspectives download:", error);
        this.$toasted.error('Error initiating perspectives report download');
        this.loadingPerspectives = false;
      }
    },

    resetReportState() {
      if (this.polling) {
        clearInterval(this.polling);
        this.polling = null;
      }
      if (this.perspectivesPolling) {
        clearInterval(this.perspectivesPolling);
        this.perspectivesPolling = null;
      }
      if (this.discrepancyPolling) {
        clearInterval(this.discrepancyPolling);
        this.discrepancyPolling = null;
      }
      this.taskId = null;
      this.perspectivesTaskId = null;
      this.discrepancyTaskId = null;
      this.downloadReady = false;
      this.perspectivesDownloadReady = false;
      this.discrepancyDownloadReady = false;
      this.loading = false;
      this.loadingPerspectives = false;
      this.loadingDiscrepancies = false;
      this.annotations = []; // Clear table data on reset
      this.perspectives = []; // Clear perspectives data on reset
      this.discrepancies = []; // Clear discrepancy data on reset
    },

    clearFilters() {
      this.selectedDatasetName = null;
      this.selectedAnnotationStatus = null;
      // Optionally regenerate report after clearing filters
      this.generateReport();
    },

    handleDatasetChange() {
      // Regenerate report when dataset changes
      this.generateReport();
    },

    handleAnnotationStatusChange() {
      // Regenerate report when annotation status changes
      this.generateReport();
    },

    fetchData() {
      // This method was a placeholder. Now it will be called by pollTaskStatus
      // No longer needed for direct data fetching on created hook.
    },

    async handleExport() {
      this.showExportDialog = false
      if (this.selectedExportFormat === 'pdf') {
        await this.exportPDF()
      } else {
        await this.exportCSV()
      }
    },

    async exportPDF() {
      if (window.event && event.preventDefault) event.preventDefault();
      try {
        const JsPDF = await this.loadJsPDF()
        const doc = new JsPDF({ orientation: 'p', unit: 'mm', format: 'a4' })
        const pageWidth = doc.internal.pageSize.getWidth()
        const margin = 20
        // Cabeçalho colorido
        doc.setFillColor(63, 81, 181)
        doc.rect(0, 0, pageWidth, 35, 'F')
        // Título
        doc.setFontSize(20)
        doc.setTextColor(255, 255, 255)
        doc.setFont(undefined, 'bold')
        doc.text('Annotation History Report', pageWidth / 2, 20, { align: 'center' })
        // Informações do projeto
        doc.setFontSize(12)
        doc.setTextColor(255, 255, 255)
        doc.setFont(undefined, 'normal')
        doc.text(`Project ID: ${this.projectId}`, margin, 30)
        // Informações de geração
        doc.setFillColor(255, 255, 255)
        doc.rect(margin, 40, pageWidth - 2 * margin, 20, 'F')
        doc.setFontSize(10)
        doc.setTextColor(0, 0, 0)
        doc.text(`Generated: ${new Date().toLocaleString()}`, margin + 5, 50)
        doc.text(`Dataset: ${this.selectedDatasetName || 'All'} | Status: ${this.selectedAnnotationStatus || 'All'}`, margin + 5, 57)
        // Estatísticas
        const totalAnnotations = this.annotations.length
        const uniqueAnnotators = [...new Set(this.annotations.map(a => a.annotator).filter(a => a !== 'N/A'))].length
        doc.setFillColor(96, 125, 139)
        doc.rect(margin, 65, pageWidth - 2 * margin, 15, 'F')
        doc.setFontSize(11)
        doc.setTextColor(255, 255, 255)
        doc.setFont(undefined, 'bold')
        doc.text(`Total Annotations: ${totalAnnotations} | Unique Annotators: ${uniqueAnnotators}`, margin + 5, 75)
        // Tabela principal
        doc.autoTable({
          startY: 85,
          head: [['Annotator', 'Label', 'Date', 'Example Text', 'Annotations']],
          body: this.filteredAnnotations.map(item => [
            item.annotator || 'N/A',
            item.label || 'N/A',
            item.date || 'N/A',
            (item.example_text || 'N/A').substring(0, 40) + '...',
            item.numberOfAnnotations || '0'
          ]),
          margin: { left: margin, right: margin },
          theme: 'grid',
          headStyles: { 
            fillColor: [63, 81, 181], 
            halign: 'center', 
            textColor: 255,
            fontSize: 10,
            fontStyle: 'bold'
          },
          bodyStyles: { 
            halign: 'left',
            fontSize: 9
          },
          alternateRowStyles: {
            fillColor: [245, 245, 245]
          },
          columnStyles: {
            0: { cellWidth: 25 },
            1: { cellWidth: 25 },
            2: { cellWidth: 25 },
            3: { cellWidth: 70 },
            4: { cellWidth: 20, halign: 'center' }
          }
        })
        // Rodapé
        const footerY = doc.internal.pageSize.getHeight() - 15
        doc.setFillColor(96, 125, 139)
        doc.rect(0, footerY, pageWidth, 15, 'F')
        doc.setFontSize(8)
        doc.setTextColor(255, 255, 255)
        doc.text('Generated by Doccano', pageWidth / 2, footerY + 8, { align: 'center' })
        // Gerar blob e abrir numa nova aba
        const pdfBlob = doc.output('blob');
        const url = URL.createObjectURL(pdfBlob);
        window.open(url, '_blank');
        this.$toasted.success('PDF opened in new tab!')
      } catch (e) {
        console.error('Failed to export annotation PDF', e)
        this.$toasted.error('Failed to export PDF')
      }
    },

    exportCSV() {
      try {
        const delimiter = ';'
        const rows = [
          ['Annotator', 'Label', 'Date', 'Example Text', 'Number of Annotations']
        ]

        // Add annotations data
        const annotationRows = this.annotations.map(item => [
          item.annotator,
          item.label,
          item.date,
          item.example_text,
          item.numberOfAnnotations
        ])
        rows.push(...annotationRows)

        // Add perspectives data if available
        if (this.perspectives && this.perspectives.length > 0) {
          rows.push([]) // Empty row as separator
          rows.push(['Perspectives'])
          rows.push(['Question', 'Answer', 'Answered By', 'Answer Date'])

          const perspectiveRows = this.perspectives.map(item => [
            item.question,
            item.answer,
            item.answered_by,
            item.answer_date
          ])
          rows.push(...perspectiveRows)
        }

        const csvContent = '\uFEFF' + // UTF-8 BOM for better compatibility (Excel)
          rows
            .map(r => r.map(item => {
              const field = String(item)
              const needsQuotes = field.includes(delimiter) || field.includes('"') || field.includes('\n')
              const escaped = field.replace(/"/g, '""')
              return needsQuotes ? `"${escaped}"` : escaped
            }).join(delimiter))
            .join('\r\n')

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `annotation_history_${new Date().toISOString()}.csv`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        this.$toasted.success('CSV exported successfully!')
      } catch (error) {
        console.error('Error exporting CSV:', error)
        this.$toasted.error('Failed to export CSV')
      }
    },

    async handlePerspectivesExport() {
      this.showPerspectivesExportDialog = false
      if (this.selectedPerspectivesExportFormat === 'pdf') {
        await this.exportPerspectivesPDF()
      } else {
        await this.exportPerspectivesCSV()
      }
    },

    async loadJsPDF() {
      if (window.jspdf && window.jspdf.jsPDF) {
        if (!window.jspdf.jsPDF.API.autoTable) {
          await new Promise((resolve, reject) => {
            const script = document.createElement('script')
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.29/jspdf.plugin.autotable.min.js'
            script.onload = resolve
            script.onerror = reject
            document.body.appendChild(script)
          })
        }
        return window.jspdf.jsPDF
      }
      await new Promise((resolve, reject) => {
        const script = document.createElement('script')
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'
        script.onload = resolve
        script.onerror = reject
        document.body.appendChild(script)
      })
      await new Promise((resolve, reject) => {
        const script = document.createElement('script')
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.29/jspdf.plugin.autotable.min.js'
        script.onload = resolve
        script.onerror = reject
        document.body.appendChild(script)
      })
      return window.jspdf.jsPDF
    },

    async exportPerspectivesPDF() {
      if (window.event) window.event.preventDefault?.();
      try {
        const JsPDF = await this.loadJsPDF()
        const doc = new JsPDF({ orientation: 'p', unit: 'mm', format: 'a4' })
        const pageWidth = doc.internal.pageSize.getWidth()
        const pageHeight = doc.internal.pageSize.getHeight()
        const margin = 20
        // Cores
        const primaryColor = [63, 81, 181] // Azul
        const secondaryColor = [96, 125, 139] // Cinza azulado
        // Cabeçalho
        doc.setFillColor(...primaryColor)
        doc.rect(0, 0, pageWidth, 40, 'F')
        // Título principal
        doc.setFontSize(24)
        doc.setTextColor(255, 255, 255)
        doc.setFont(undefined, 'bold')
        doc.text('Perspectives Report', pageWidth / 2, 25, { align: 'center' })
        // Informações do projeto
        doc.setFontSize(12)
        doc.setTextColor(255, 255, 255)
        doc.setFont(undefined, 'normal')
        doc.text(`Project ID: ${this.projectId}`, margin, 35)
        // Informações de geração
        doc.setFillColor(255, 255, 255)
        doc.rect(margin, 45, pageWidth - 2 * margin, 25, 'F')
        doc.setFontSize(10)
        doc.setTextColor(0, 0, 0)
        doc.text(`Generated on: ${new Date().toLocaleString()}`, margin + 5, 55)
        doc.text(`Dataset: ${this.selectedDatasetName || 'All datasets'}`, margin + 5, 62)
        doc.text(`Annotation Status: ${this.selectedAnnotationStatus || 'All'}`, margin + 5, 69)
        // Estatísticas
        const totalPerspectives = this.perspectives.length
        const uniquePerspectiveQuestions = [...new Set(this.perspectives.map(p => p.question).filter(q => q !== 'N/A'))].length
        const uniquePerspectiveAnswers = [...new Set(this.perspectives.map(p => p.answer).filter(a => a !== 'N/A'))].length
        // Box de estatísticas
        const statsY = 80
        doc.setFillColor(...secondaryColor)
        doc.rect(margin, statsY, pageWidth - 2 * margin, 20, 'F')
        doc.setFontSize(12)
        doc.setTextColor(255, 255, 255)
        doc.setFont(undefined, 'bold')
        doc.text('Statistics', margin + 5, statsY + 8)
        doc.setFontSize(10)
        doc.setFont(undefined, 'normal')
        doc.text(`Total Perspectives: ${totalPerspectives}`, margin + 5, statsY + 15)
        doc.text(`Unique Perspective Questions: ${uniquePerspectiveQuestions}`, margin + 120, statsY + 15)
        doc.text(`Unique Perspective Answers: ${uniquePerspectiveAnswers}`, margin + 235, statsY + 15)
        // Tabela de perspectives
        const tableY = statsY + 30
        doc.autoTable({
          startY: tableY,
          head: [[
            'Perspective Question',
            'Perspective Answer',
            'Answered By',
            'Answer Date'
          ]],
          body: this.perspectives.map(item => [
            (item.question || 'N/A').substring(0, 40) + (item.question && item.question.length > 40 ? '...' : ''),
            (item.answer || 'N/A').substring(0, 30) + (item.answer && item.answer.length > 30 ? '...' : ''),
            item.answered_by || 'N/A',
            item.answer_date || 'N/A'
          ]),
          margin: { left: margin, right: margin },
          theme: 'grid',
          headStyles: { 
            fillColor: primaryColor, 
            halign: 'center', 
            valign: 'middle', 
            textColor: 255,
            fontSize: 10,
            fontStyle: 'bold'
          },
          bodyStyles: { 
            halign: 'left',
            fontSize: 9,
            textColor: 0
          },
          alternateRowStyles: {
            fillColor: [245, 245, 245]
          },
          styles: { 
            fontSize: 9,
            cellPadding: 3
          },
          columnStyles: {
            0: { cellWidth: 50 }, // Question
            1: { cellWidth: 40 }, // Answer
            2: { cellWidth: 30 }, // Answered By
            3: { cellWidth: 35 }  // Answer Date
          }
        })
        // Rodapé
        const footerY = pageHeight - 20
        doc.setFillColor(...secondaryColor)
        doc.rect(0, footerY, pageWidth, 20, 'F')
        doc.setFontSize(8)
        doc.setTextColor(255, 255, 255)
        doc.setFont(undefined, 'normal')
        doc.text('Generated by Doccano Annotation Platform', pageWidth / 2, footerY + 8, { align: 'center' })
        doc.text(`Page 1 of 1`, pageWidth - margin, footerY + 8, { align: 'right' })
        // Gerar blob e abrir numa nova aba
        const pdfBlob = doc.output('blob');
        const url = URL.createObjectURL(pdfBlob);
        window.open(url, '_blank');
        this.$toasted.success('PDF opened in new tab!')
      } catch (e) {
        console.error('Failed to export perspectives PDF', e)
        this.$toasted.error('Failed to export perspectives PDF')
      }
    },

    exportPerspectivesCSV() {
      try {
        const delimiter = ';'
        const rows = [
          ['Perspective Question', 'Perspective Answer', 'Answered By', 'Answer Date']
        ]

        // Add perspectives data
        const perspectiveRows = this.perspectives.map(item => [
          item.question,
          item.answer,
          item.answered_by,
          item.answer_date
        ])
        rows.push(...perspectiveRows)

        const csvContent = '\uFEFF' + // UTF-8 BOM for better compatibility (Excel)
          rows
            .map(r => r.map(item => {
              const field = String(item)
              const needsQuotes = field.includes(delimiter) || field.includes('"') || field.includes('\n')
              const escaped = field.replace(/"/g, '""')
              return needsQuotes ? `"${escaped}"` : escaped
            }).join(delimiter))
            .join('\r\n')

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `project-${this.projectId}-perspectives-report.csv`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        this.$toasted.success('Perspectives CSV exported successfully!')
      } catch (error) {
        console.error('Error exporting perspectives CSV:', error)
        this.$toasted.error('Failed to export perspectives CSV')
      }
    },

    async handleDiscrepanciesExport() {
      this.showDiscrepanciesExportDialog = false
      if (this.selectedDiscrepanciesExportFormat === 'pdf') {
        await this.exportDiscrepanciesPDF()
      } else {
        await this.exportDiscrepanciesCSV()
      }
    },

    async exportDiscrepanciesPDF() {
      if (window.event) window.event.preventDefault?.();
      try {
        const JsPDF = await this.loadJsPDF()
        const doc = new JsPDF({ orientation: 'p', unit: 'mm', format: 'a4' })
        const pageWidth = doc.internal.pageSize.getWidth()
        const pageHeight = doc.internal.pageSize.getHeight()
        const margin = 20
        // Cores
        const primaryColor = [63, 81, 181] // Azul
        const secondaryColor = [96, 125, 139] // Cinza azulado
        // Cabeçalho
        doc.setFillColor(...primaryColor)
        doc.rect(0, 0, pageWidth, 40, 'F')
        // Título principal
        doc.setFontSize(24)
        doc.setTextColor(255, 255, 255)
        doc.setFont(undefined, 'bold')
        doc.text('Discrepancy Report', pageWidth / 2, 25, { align: 'center' })
        // Informações do projeto
        doc.setFontSize(12)
        doc.setTextColor(255, 255, 255)
        doc.setFont(undefined, 'normal')
        doc.text(`Project ID: ${this.projectId}`, margin, 35)
        // Informações de geração
        doc.setFillColor(255, 255, 255)
        doc.rect(margin, 45, pageWidth - 2 * margin, 25, 'F')
        doc.setFontSize(10)
        doc.setTextColor(0, 0, 0)
        doc.text(`Generated on: ${new Date().toLocaleString()}`, margin + 5, 55)
        doc.text(`Dataset: ${this.selectedDatasetName || 'All datasets'}`, margin + 5, 62)
        // Estatísticas
        const statsY = 80
        doc.setFillColor(...secondaryColor)
        doc.rect(margin, statsY, pageWidth - 2 * margin, 15, 'F')
        doc.setFontSize(12)
        doc.setTextColor(255, 255, 255)
        doc.setFont(undefined, 'bold')
        doc.text('Statistics', margin + 5, statsY + 10)
        // Tabela de discrepancies
        const tableY = statsY + 20
        doc.autoTable({
          startY: tableY,
          head: [[
            'Example ID',
            'Text',
            'Is Discrepancy',
            'Max. Percentage'
          ]],
          body: this.discrepancies.map(item => [
            item.example_id || 'N/A',
            (item.text || 'N/A').substring(0, 40) + (item.text && item.text.length > 40 ? '...' : ''),
            item.is_discrepancy ? 'Yes' : 'No',
            item.max_percentage != null ? item.max_percentage.toFixed(2) + '%' : 'N/A'
          ]),
          margin: { left: margin, right: margin },
          theme: 'grid',
          headStyles: { 
            fillColor: primaryColor, 
            halign: 'center', 
            valign: 'middle', 
            textColor: 255,
            fontSize: 10,
            fontStyle: 'bold'
          },
          bodyStyles: { 
            halign: 'left',
            fontSize: 9,
            textColor: 0
          },
          alternateRowStyles: {
            fillColor: [245, 245, 245]
          },
          styles: { 
            fontSize: 9,
            cellPadding: 3
          },
          columnStyles: {
            0: { cellWidth: 20 }, // Example ID
            1: { cellWidth: 50 }, // Text
            2: { cellWidth: 25 }, // Is Discrepancy
            3: { cellWidth: 30 }, // Max. Percentage
          }
        })
        // Rodapé
        const footerY = pageHeight - 20
        doc.setFillColor(...secondaryColor)
        doc.rect(0, footerY, pageWidth, 20, 'F')
        doc.setFontSize(8)
        doc.setTextColor(255, 255, 255)
        doc.setFont(undefined, 'normal')
        doc.text('Generated by Doccano Annotation Platform', pageWidth / 2, footerY + 8, { align: 'center' })
        doc.text(`Page 1 of 1`, pageWidth - margin, footerY + 8, { align: 'right' })
        // Gerar blob e abrir numa nova aba
        const pdfBlob = doc.output('blob');
        const url = URL.createObjectURL(pdfBlob);
        window.open(url, '_blank');
        this.$toasted.success('PDF opened in new tab!')
      } catch (e) {
        console.error('Failed to export discrepancies PDF', e)
        this.$toasted.error('Failed to export discrepancies PDF')
      }
    },

    exportDiscrepanciesCSV() {
      try {
        const delimiter = ';'
        const rows = [
          ['Example ID', 'Text', 'Is Discrepancy', 'Max. Percentage']
        ]
        // Add discrepancies data
        const discrepancyRows = this.discrepancies.map(item => [
          item.example_id,
          item.text,
          item.is_discrepancy ? 'Yes' : 'No',
          item.max_percentage != null ? item.max_percentage.toFixed(2) + '%' : 'N/A'
        ])
        rows.push(...discrepancyRows)
        const csvContent = '\uFEFF' + // UTF-8 BOM for better compatibility (Excel)
          rows
            .map(r => r.map(item => {
              const field = String(item)
              const needsQuotes = field.includes(delimiter) || field.includes('"') || field.includes('\n')
              const escaped = field.replace(/"/g, '""')
              return needsQuotes ? `"${escaped}"` : escaped
            }).join(delimiter))
            .join('\r\n')
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `project-${this.projectId}-discrepancies-report.csv`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        this.$toasted.success('Discrepancies CSV exported successfully!')
      } catch (error) {
        console.error('Error exporting discrepancies CSV:', error)
        this.$toasted.error('Failed to export discrepancies CSV')
      }
    },
  },
};
</script>

<style scoped>
</style> 