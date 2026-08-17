<template>
  <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg shadow-md">
    <h2 class="text-xl font-bold mb-4 text-white">Admin Panel</h2>
    <div class="space-y-3">
      <div
        v-for="request in requests"
        :key="request.id"
        class="border border-gray-600 rounded p-3 bg-gray-700">
        <h3 class="font-medium text-white">{{ request.title }}</h3>
        <p v-if="request.author" class="text-xs text-gray-400">by {{ request.author }}</p>
        <p class="text-sm text-gray-300">{{ request.description }}</p>

        <div class="flex justify-between items-center mt-2">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-900 text-blue-200">
            {{ request.media_type }}
          </span>
          <div class="flex space-x-2">
            <button
              v-if="request.status === 'PENDING'"
              @click="startApprove(request)"
              class="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700">
              Approve
            </button>
            <button
              @click="updateStatus(request.id, 'FULFILLED')"
              class="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700">
              Fulfill
            </button>
            <button
              @click="updateStatus(request.id, 'DENIED')"
              class="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700">
              Deny
            </button>
          </div>
        </div>

        <!-- Approve picker: shown while choosing a target for this request -->
        <div v-if="approvingId === request.id" class="mt-3 border-t border-gray-600 pt-3">
          <label class="block text-xs text-gray-300 mb-1">Send to media manager</label>
          <div class="flex gap-2">
            <select v-model="selectedInstanceId" class="flex-1 px-2 py-1 text-sm bg-gray-800 border border-gray-600 rounded text-white">
              <option :value="null">Approve only (no push)</option>
              <option v-for="i in eligible" :key="i.id" :value="i.id">{{ i.name }} ({{ i.service }})</option>
            </select>
            <button @click="doApprove(request, selectedInstanceId)" class="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700">Confirm</button>
            <button @click="approvingId = null" class="px-3 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-500">Cancel</button>
          </div>
        </div>

        <div class="mt-2 flex items-center gap-2 flex-wrap">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-600 text-gray-200">
            {{ request.status }}
          </span>
          <span v-if="request.target_service" class="text-xs text-green-400">
            → {{ request.target_service }}<template v-if="request.external_ref"> #{{ request.external_ref }}</template>
          </span>
        </div>
        <p v-if="request.fulfillment_detail" class="mt-1 text-xs text-gray-400">
          {{ request.fulfillment_detail }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { useRequestsStore } from "../stores/requests";
import axios from "axios";
import { API_URL } from "../utils/api";

export default {
  name: "AdminPanel",
  props: {
    requests: Array,
  },
  data() {
    return {
      approvingId: null,
      selectedInstanceId: null,
      eligible: [],
    };
  },
  created() {
    this.requestsStore = useRequestsStore();
  },
  methods: {
    _replace(updated) {
      const idx = this.requestsStore.requests.findIndex((r) => r.id === updated.id);
      if (idx !== -1) this.requestsStore.requests[idx] = updated;
    },

    async startApprove(request) {
      this.approvingId = request.id;
      this.selectedInstanceId = null;
      this.eligible = [];
      try {
        const { data } = await axios.get(`${API_URL}/media-managers/eligible`, {
          params: { media_type: request.media_type },
        });
        this.eligible = data;
        // Nothing to route to — approve straight away (manual workflow).
        if (data.length === 0) {
          await this.doApprove(request, null);
        }
      } catch (error) {
        console.error("Failed to load eligible managers:", error);
      }
    },

    async doApprove(request, instanceId) {
      try {
        const { data } = await axios.post(
          `${API_URL}/admin/requests/${request.id}/approve`,
          { instance_id: instanceId }
        );
        this._replace(data);
      } catch (error) {
        console.error("Failed to approve:", error);
      } finally {
        this.approvingId = null;
      }
    },

    async updateStatus(requestId, status) {
      try {
        const { data } = await axios.patch(
          `${API_URL}/admin/requests/${requestId}/status`,
          { status }
        );
        this._replace(data);
      } catch (error) {
        console.error("Failed to update status:", error);
      }
    },
  },
};
</script>
