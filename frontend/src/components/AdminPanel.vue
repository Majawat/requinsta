<template>
  <div>
    <div v-if="!requests || requests.length === 0" class="card p-6 text-center text-slate-400 text-sm">
      No requests yet.
    </div>
    <div v-else class="space-y-3">
      <div
        v-for="request in requests"
        :key="request.id"
        class="card p-4"
      >
        <div class="flex gap-3">
          <MediaThumb :cover="request.cover_url" :type="request.media_type" :w="44" :h="62" />
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <h3 class="font-semibold text-slate-100 truncate">{{ request.title }}</h3>
                <p class="text-[13px] text-slate-400 truncate">
                  <template v-if="request.author">{{ request.author }}</template><template v-if="request.author && request.year"> · </template><template v-if="request.year">{{ request.year }}</template>
                </p>
              </div>
              <StatusPill :status="request.status" small class="flex-none" />
            </div>
            <p v-if="request.description" class="text-[13px] text-slate-400 mt-1.5 line-clamp-2">{{ request.description }}</p>

            <div class="flex items-center gap-2 mt-2 flex-wrap">
              <TypeBadge :type="request.media_type" />
              <span v-if="request.target_service" class="text-xs text-emerald-400">
                → {{ request.target_service }}<template v-if="request.external_ref"> #{{ request.external_ref }}</template>
              </span>
            </div>
            <p v-if="request.fulfillment_detail" class="mt-1.5 text-xs text-slate-500 line-clamp-2">{{ request.fulfillment_detail }}</p>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-2 mt-3">
          <button v-if="request.status === 'PENDING'" @click="startApprove(request)" class="btn-primary btn-sm">Approve</button>
          <button v-if="request.status !== 'FULFILLED'" @click="updateStatus(request.id, 'FULFILLED')" class="btn-secondary btn-sm">Mark fulfilled</button>
          <button v-if="request.status !== 'DENIED'" @click="updateStatus(request.id, 'DENIED')" class="btn-deny btn-sm">Deny</button>
        </div>

        <!-- Approve picker: shown while choosing a target for this request -->
        <div v-if="approvingId === request.id" class="mt-3 border-t border-slate-800 pt-3">
          <label class="label">Send to media manager</label>
          <div class="flex flex-col sm:flex-row gap-2">
            <select v-model="selectedInstanceId" class="input flex-1">
              <option :value="null">Approve only (no push)</option>
              <option v-for="i in eligible" :key="i.id" :value="i.id">{{ i.name }} ({{ i.service }})</option>
            </select>
            <div class="flex gap-2">
              <button @click="doApprove(request, selectedInstanceId)" class="btn-primary btn-sm">Confirm</button>
              <button @click="approvingId = null" class="btn-ghost btn-sm">Cancel</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useRequestsStore } from "../stores/requests";
import axios from "axios";
import { API_URL } from "../utils/api";
import MediaThumb from "./ui/MediaThumb.vue";
import StatusPill from "./ui/StatusPill.vue";
import TypeBadge from "./ui/TypeBadge.vue";

export default {
  name: "AdminPanel",
  components: { MediaThumb, StatusPill, TypeBadge },
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
