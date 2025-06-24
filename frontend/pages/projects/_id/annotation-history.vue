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
        <v-btn color="primary" class="mr-2" :loading="loading"
         :disabled="loading" @click="generateReport">
          <v-icon left>mdi-file-document-outline</v-icon>
          Generate Report
        </v-btn>
        <v-btn color="primary" outlined :disabled="!downloadReady" @click="showExportDialog = true">
          <v-icon left>mdi-download</v-icon>
          Export Report
        </v-btn>
      </v-card-title>

      <v-card-text>
        <!-- Content for Annotations Tab -->
        <v-tabs-items v-model="selectedTab">
          <v-tab-item value="tab-annotations">
            <template v-if="selectedReportType === 'Annotation History'">
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
                :items="annotations"
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
                <v-btn color="primary" outlined :disabled="!perspectivesDownloadReady"
                 @click="showExportPerspectivesDialog = true">
                  <v-icon left>mdi-download</v-icon>
                  Export Perspectives
                </v-btn>
              </v-card-title>

              <v-data-table
                :headers="perspectiveHeaders"
                :items="perspectives"
                :loading="loadingPerspectives"
                class="elevation-1"
              >
                <template #no-data>
                  <v-alert
                    type="info"
                    text
                    class="ma-4"
                  >
                    <div class="text-center">
                      <v-icon large color="info" class="mb-2">mdi-information</v-icon>
                      <div class="text-h6 mb-2">No Perspective Data Found</div>
                      <div class="text-body-2">
                        This project doesn't have any perspective data to display.
                        <br>
                        To see data here, you need to:
                        <ul class="text-left mt-2">
                          <li>Create perspectives in the project settings</li>
                          <li>Answer perspective questions for examples</li>
                          <li>Generate the report again</li>
                        </ul>
                      </div>
                    </div>
                  </v-alert>
                </template>
              </v-data-table>
            </template>
            <template v-else>
              <!-- Placeholder for Discrepancy Report content under Annotations tab -->
              <p>Content for Discrepancy Report (Annotations view)</p>
            </template>
          </v-tab-item>

          <!-- Content for Annotators Tab -->
          <v-tab-item value="tab-annotators">
            <!-- This content will change based on selectedReportType too -->
            <template v-if="selectedReportType === 'Annotation History'">
              <p>Content for Annotation History (Annotators view)</p>
            </template>
            <template v-else>
              <p>Content for Discrepancy Report (Annotators view)</p>
            </template>
          </v-tab-item>
        </v-tabs-items>
      </v-card-text>
    </v-card>

    <!-- Export Format Dialog -->
    <v-dialog v-model="showExportDialog" max-width="400" @submit.prevent>
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
          <v-btn color="primary" type="button" @click="handleExport($event)">
            <v-icon left>mdi-download</v-icon>
            Export
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Export Format Dialog for Perspectives -->
    <v-dialog v-model="showExportPerspectivesDialog" max-width="400" @submit.prevent>
      <v-card>
        <v-card-title class="text-h5">
          <v-icon left color="primary">mdi-download</v-icon>
          Choose Export Format
        </v-card-title>
        <v-card-text>
          <v-radio-group v-model="selectedExportPerspectivesFormat" class="mt-4">
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
          <v-btn text @click="showExportPerspectivesDialog = false">Cancel</v-btn>
          <v-btn color="primary" type="button" @click="handleExportPerspectives($event)">
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
      selectedReportType: 'Annotation History', // Default selected report type
      reportTypes: ['Annotation History', 'Discrepancy Report'], // Report types
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
      annotations: [], // Initialize as empty array
      perspectives: [], // Initialize perspectives array
      loading: false,
      loadingPerspectives: false,
      taskId: null,
      perspectivesTaskId: null,
      polling: null,
      perspectivesPolling: null,
      downloadReady: false,
      perspectivesDownloadReady: false,
      mdiMagnify,
      showExportDialog: false,
      selectedExportFormat: 'pdf',
      showExportPerspectivesDialog: false,
      selectedExportPerspectivesFormat: 'pdf',
      discrepancies: [],
      loadingDiscrepancy: false,
      discrepancyTaskId: null,
      discrepancyPolling: null,
      exportDiscrepancyReady: false,
    };
  },
  computed: {
    projectId() {
      return this.$route.params.id
    }
  },
  created() {
    this.fetchDatasetNames();
    // this.fetchData(); // No longer calling fetchData directly on created
  },
  beforeDestroy() {
    clearInterval(this.polling);
    clearInterval(this.perspectivesPolling);
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

    handleDatasetChange() {
      // Regenerate report when dataset changes
      if (this.selectedDatasetName) {
        this.generateReport();
      }
    },

    handleAnnotationStatusChange() {
      // Regenerate report when annotation status changes
      if (this.selectedAnnotationStatus) {
        this.generateReport();
      }
    },

    async generateReport() {
      if (this.selectedReportType === 'Discrepancy Report') {
        await this.generateDiscrepancyReport();
        return;
      }
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
        console.error("Error generating report:", error);
        this.$toasted.error('Error generating report');
        this.loading = false;
      }
    },

    async generatePerspectivesReport() {
      this.loadingPerspectives = true;
      this.perspectivesDownloadReady = false;
      this.perspectives = []; // Clear previous perspectives
      try {
        console.log("Starting perspectives report generation for project:", this.projectId);
        console.log("Selected dataset:", this.selectedDatasetName);
        
        // Use the specific perspective history endpoint instead of annotation history
        const response = await this.$axios.post(
          `/v1/projects/${this.projectId}/perspective-history`,
          {
            datasetName: this.selectedDatasetName
          }
        );
        
        console.log("Perspective history API response:", response.data);
        this.perspectivesTaskId = response.data.task_id;
        console.log("Perspectives task ID:", this.perspectivesTaskId);
        
        // Start polling for the task status
        this.pollPerspectivesTaskStatus();
      } catch (error) {
        console.error("Error generating perspectives report:", error);
        this.$toasted.error('Error generating perspectives report');
        this.loadingPerspectives = false;
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
              
              this.annotations = data.map(item => ({
                ...item,
                date: new Date(item.date).toLocaleString() // Format date
              }));
              
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
      
      let attempts = 0;
      const maxAttempts = 60; // 60 seconds timeout (60 * 1000ms)
      
      console.log("Starting polling for perspectives task:", this.perspectivesTaskId);
      
      this.perspectivesPolling = setInterval(async () => {
        if (!this.perspectivesTaskId) {
          console.error("No perspectives task ID available");
          clearInterval(this.perspectivesPolling);
          this.perspectivesPolling = null;
          return;
        }

        attempts++;
        console.log(`Polling perspectives task ${this.perspectivesTaskId}, attempt ${attempts}/${maxAttempts}`);

        // Check for timeout
        if (attempts >= maxAttempts) {
          console.error("Perspectives task polling timed out");
          clearInterval(this.perspectivesPolling);
          this.perspectivesPolling = null;
          this.loadingPerspectives = false;
          this.$toasted.error('Perspectives report generation timed out');
          return;
        }

        try {
          const res = await this.$repositories.taskStatus.get(this.perspectivesTaskId);
          console.log("Task status response for perspectives:", res);

          if (res && res.ready) {
            console.log("Task is ready, processing result...");
            clearInterval(this.perspectivesPolling);
            this.perspectivesPolling = null;
            this.loadingPerspectives = false;
            
            if (!res.error) { // Consider success if ready and no error
              try {
                // Fetch the actual data for the table using the specific perspective endpoint
                const dataResponse = await this.$axios.get(
                  `/v1/projects/${this.projectId}/perspective-history-data`,
                  {
                    params: { taskId: this.perspectivesTaskId }
                  }
                );
                
                console.log("Raw data response:", dataResponse);
                
                // Validate response structure - check if dataResponse.data exists first
                if (dataResponse && dataResponse.data) {
                  console.log("Response data structure:", dataResponse.data);
                  console.log("Success field:", dataResponse.data.success);
                  console.log("Data field:", dataResponse.data.data);
                  
                  if (dataResponse.data.success === true) {
                    const data = dataResponse.data.data || [];
                    console.log("Raw data fetched for perspectives:", data);
                    console.log("Data length:", data.length);
                    
                    if (data.length === 0) {
                      console.log("No perspective data found - this might be normal if no perspectives exist");
                      this.$toasted.success('No perspective data found for this project/dataset');
                    }
                    
                    // Process perspectives data - the data should already be in the correct format
                    this.perspectives = data.map(item => ({
                      question: item.question,
                      answer: item.answer,
                      answered_by: item.answered_by,
                      answer_date: new Date(item.answer_date).toLocaleString()
                    }));
                    
                    console.log("Fetched perspectives (after processing):", this.perspectives);
                    this.perspectivesDownloadReady = true;
                    this.$toasted.success('Perspectives report generated successfully!');
                  } else if (dataResponse.data.success === false) {
                    // Backend returned an error
                    const errorMessage = dataResponse.data.error || 'Unknown error from backend';
                    console.error("Backend error:", errorMessage);
                    this.$toasted.error(`Error: ${errorMessage}`);
                  } else {
                    // Unexpected response format
                    console.error("Unexpected response format:", dataResponse.data);
                    this.$toasted.error('Unexpected response format from server');
                  }
                } else {
                  // No data in response
                  console.error("No data in response:", dataResponse);
                  this.$toasted.error('No data received from server');
                }
              } catch (dataError) {
                console.error("Error fetching perspectives data:", dataError);
                
                // Check if it's a 404 or 500 error
                if (dataError.response) {
                  const status = dataError.response.status;
                  const errorData = dataError.response.data;
                  
                  if (status === 404) {
                    this.$toasted.error('Report file not found. Please try generating the report again.');
                  } else if (status === 500) {
                    const errorMessage = errorData?.error || 'Server error occurred';
                    this.$toasted.error(`Server error: ${errorMessage}`);
                  } else {
                    this.$toasted.error(`HTTP ${status}: ${errorData?.error || 'Unknown error'}`);
                  }
                } else {
                  this.$toasted.error('Network error while fetching perspectives data');
                }
              }
            } else { // Consider failure if ready and has error
              console.error("Task failed with error:", res?.error);
              const errorMessage = res?.error?.text || res?.error || 'Unknown error';
              this.$toasted.error(`Error generating perspectives report: ${errorMessage}`);
            }
          } else {
            console.log("Task not ready yet, continuing to poll...");
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
              // Download the file as a blob
              const fileResponse = await this.$axios.get(
                `/v1/projects/${this.projectId}/annotation-history`,
                {
                  params: { taskId: downloadTaskId },
                  responseType: 'blob'
                }
              );
              const blob = new Blob([fileResponse.data], { type: 'text/csv;charset=utf-8;' });
              const url = window.URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.setAttribute('download', `annotation_history_${new Date().toISOString()}.csv`);
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              window.URL.revokeObjectURL(url);
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
        // Use the specific perspective history endpoint instead of annotation history
        const response = await this.$axios.post(
          `/v1/projects/${this.projectId}/perspective-history`,
          {
            datasetName: this.selectedDatasetName
          }
        );
        const downloadTaskId = response.data.task_id;

        let downloadPolling = null;
        downloadPolling = setInterval(async () => {
          const res = await this.$repositories.taskStatus.get(downloadTaskId);
          console.log("Download task status response for perspectives:", res);
          if (res && res.ready) {
            if (!res.error) { // Consider success if ready and no error
              clearInterval(downloadPolling);
              this.loadingPerspectives = false;
              // Download the file using the perspective history endpoint as a blob
              const fileResponse = await this.$axios.get(
                `/v1/projects/${this.projectId}/perspective-history`,
                {
                  params: { taskId: downloadTaskId },
                  responseType: 'blob'
                }
              );
              const blob = new Blob([fileResponse.data], { type: 'text/csv;charset=utf-8;' });
              const url = window.URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.setAttribute('download', `perspectives_report_${new Date().toISOString()}.csv`);
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              window.URL.revokeObjectURL(url);
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
      this.taskId = null;
      this.perspectivesTaskId = null;
      this.downloadReady = false;
      this.perspectivesDownloadReady = false;
      this.loading = false;
      this.loadingPerspectives = false;
      this.annotations = []; // Clear table data on reset
      this.perspectives = []; // Clear perspectives data on reset
    },

    clearFilters() {
      this.selectedDatasetName = null;
      this.selectedAnnotationStatus = null;
      // Optionally regenerate report after clearing filters
      this.generateReport();
    },

    fetchData() {
      // This method was a placeholder. Now it will be called by pollTaskStatus
      // No longer needed for direct data fetching on created hook.
    },

    async handleExport(event) {
      if (event && event.preventDefault) event.preventDefault();
      this.showExportDialog = false
      if (this.selectedExportFormat === 'pdf') {
        await this.exportPDF()
      } else {
        await this.exportCSV()
      }
    },

    async exportPDF() {
      if (window.event) window.event.preventDefault?.();
      try {
        const JsPDF = await this.loadJsPDF()
        const doc = new JsPDF({ orientation: 'p', unit: 'mm', format: 'a4' })
        const pageWidth = doc.internal.pageSize.getWidth()
        const margin = 18
        doc.setFontSize(16)
        doc.setTextColor(63, 81, 181)
        doc.setFont(undefined, 'bold')
        doc.text('Annotation History Report' + (this.selectedDatasetName ? ` - ${this.selectedDatasetName}` : ''), pageWidth / 2, 18, { align: 'center' })
        doc.setFontSize(11)
        doc.setTextColor(0)
        doc.setFont(undefined, 'normal')
        doc.text(`Generated on: ${new Date().toLocaleString()} Annotation Status: ${this.selectedAnnotationStatus || 'All'}`, margin, 28)
        doc.autoTable({
          startY: 36,
          head: [
            this.headers.map(h => h.text)
          ],
          body: this.annotations.map(item => [
            item.annotator,
            item.label,
            item.date,
            item.example_text,
            item.numberOfAnnotations,
            item.perspectives // Se existir esta coluna, senão remove
          ]),
          margin: { left: margin, right: margin },
          theme: 'grid',
          headStyles: { fillColor: [63, 81, 181], halign: 'center', valign: 'middle', textColor: 255 },
          bodyStyles: { halign: 'center' },
          styles: { fontSize: 9 }
        })
        doc.save(`annotation_history_${new Date().toISOString()}.pdf`)
        this.$toasted.success('PDF exported successfully!')
      } catch (e) {
        console.error('Failed to export annotation PDF', e)
        this.$toasted.error('Failed to export PDF')
      }
    },

    exportCSV() {
      if (window.event) window.event.preventDefault?.();
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

    async handleExportPerspectives(event) {
      if (event && event.preventDefault) event.preventDefault();
      this.showExportPerspectivesDialog = false
      if (this.selectedExportPerspectivesFormat === 'pdf') {
        await this.generatePerspectivesPdf()
      } else {
        await this.downloadPerspectivesReport()
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

    async generatePerspectivesPdf() {
      if (window.event) window.event.preventDefault?.();
      try {
        const JsPDF = await this.loadJsPDF()
        const doc = new JsPDF({ orientation: 'p', unit: 'mm', format: 'a4' })
        const pageWidth = doc.internal.pageSize.getWidth()
        const margin = 18
        doc.setFontSize(16)
        doc.setTextColor(63, 81, 181)
        doc.setFont(undefined, 'bold')
        doc.text('Perspectives Report', pageWidth / 2, 18, { align: 'center' })
        doc.setFontSize(11)
        doc.setTextColor(0)
        doc.setFont(undefined, 'normal')
        doc.text(`Project ID: ${this.projectId}`, margin, 28)
        doc.text(`Generated: ${new Date().toLocaleString()}`, margin, 36)
        doc.autoTable({
          startY: 44,
          head: [[
            'Perspective Question',
            'Perspective Answer',
            'Answered By',
            'Answer Date'
          ]],
          body: this.perspectives.map(item => [
            item.question,
            item.answer,
            item.answered_by,
            item.answer_date
          ]),
          margin: { left: margin, right: margin },
          theme: 'grid',
          headStyles: { fillColor: [63, 81, 181], halign: 'center', valign: 'middle', textColor: 255 },
          bodyStyles: { halign: 'center' },
          styles: { fontSize: 9 }
        })
        doc.save(`project-${this.projectId}-perspectives-report.pdf`)
        this.$toasted.success('PDF exported successfully!')
      } catch (e) {
        console.error('Failed to export perspectives PDF', e)
        this.$toasted.error('Failed to export perspectives PDF')
      }
    },

    async generateDiscrepancyReport() {
      this.loadingDiscrepancy = true;
      this.exportDiscrepancyReady = false;
      this.discrepancies = [];
      try {
        const response = await this.$axios.post(`/v1/projects/${this.projectId}/discrepancy-history`, {
          datasetName: this.selectedDatasetName
        });
        this.discrepancyTaskId = response.data.task_id;
        this.pollDiscrepancyTaskStatus();
      } catch (error) {
        console.error('Error generating discrepancy report:', error);
        this.$toasted.error('Error generating discrepancy report');
        this.loadingDiscrepancy = false;
      }
    },

    pollDiscrepancyTaskStatus() {
      if (this.discrepancyPolling) {
        clearInterval(this.discrepancyPolling);
        this.discrepancyPolling = null;
      }
      let attempts = 0;
      const maxAttempts = 60;
      this.discrepancyPolling = setInterval(async () => {
        if (!this.discrepancyTaskId) {
          clearInterval(this.discrepancyPolling);
          this.discrepancyPolling = null;
          return;
        }
        attempts++;
        if (attempts >= maxAttempts) {
          clearInterval(this.discrepancyPolling);
          this.discrepancyPolling = null;
          this.loadingDiscrepancy = false;
          this.$toasted.error('Discrepancy report generation timed out');
          return;
        }
        try {
          const res = await this.$axios.get(`/v1/projects/${this.projectId}/discrepancy-history-data`, {
            params: { taskId: this.discrepancyTaskId },
            validateStatus: _ => true // Aceita todos os status
          });
          if (res.status === 202 || (res.data && res.data.status === 'Not ready')) {
            // Ainda não está pronto, continua polling
            this.loadingDiscrepancy = true;
            return;
          } else if (res.status === 200) {
            clearInterval(this.discrepancyPolling);
            this.discrepancyPolling = null;
            this.loadingDiscrepancy = false;
            this.exportDiscrepancyReady = true;
            this.discrepancies = res.data;
            console.log('Discrepancy data loaded:', this.discrepancies);
            this.$toasted.success('Discrepancy report generated successfully!');
          } else {
            // Outro erro
            throw new Error(res.data?.message || 'Unknown error');
          }
        } catch (error) {
          console.error('Error polling discrepancy report:', error);
          clearInterval(this.discrepancyPolling);
          this.discrepancyPolling = null;
          this.loadingDiscrepancy = false;
          this.$toasted.error('Error polling discrepancy report');
        }
      }, 1000);
    },
  },
};
</script>

<style scoped>
</style> 