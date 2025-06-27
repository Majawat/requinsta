<template>
  <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg shadow-md">
    <h2 class="text-xl font-bold mb-4 text-white">Admin Panel</h2>
    <div class="space-y-3">
      <div
        v-for="request in requests"
        :key="request.id"
        class="border border-gray-600 rounded p-3 bg-gray-700">
        <h3 class="font-medium text-white">{{ request.title }}</h3>
        <p class="text-sm text-gray-300">{{ request.description }}</p>
        <div class="flex justify-between items-center mt-2">
          <span
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-900 text-blue-200">
            {{ request.media_type }}
          </span>
          <div class="flex space-x-2">
            <button
              @click="updateStatus(request.id, 'APPROVED')"
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
        <span
          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-600 text-gray-200 mt-2">
          {{ request.status }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { useRequestsStore } from "../stores/requests";
import axios from "axios";

export default {
  name: "AdminPanel",
  props: {
    requests: Array,
  },
  methods: {
    async updateStatus(requestId, status) {
      try {
        await axios.patch(`http://localhost:8000/api/v1/admin/requests/${requestId}/status`, {
          status: status,
        });

        const requestsStore = useRequestsStore();
        await requestsStore.fetchRequests();
      } catch (error) {
        console.error("Failed to update status:", error);
      }
    },
  },
};
</script>
