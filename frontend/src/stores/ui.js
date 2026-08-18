import { defineStore } from "pinia";

let seq = 0;

// Lightweight UI state: toasts (optimistic feedback with optional Undo) and the
// currently-open request-detail sheet. Kept out of the domain stores so any view
// can raise a toast or open the sheet without prop-drilling.
export const useUiStore = defineStore("ui", {
  state: () => ({
    toasts: [],
    // The request object currently shown in the detail sheet, or null.
    sheetRequest: null,
  }),

  actions: {
    // toast("Requested X", { type: "success", actionLabel: "Undo", onAction, timeout })
    toast(message, opts = {}) {
      const id = ++seq;
      const t = {
        id,
        message,
        type: opts.type || "success",
        actionLabel: opts.actionLabel || null,
        onAction: opts.onAction || null,
        timeout: opts.timeout ?? 4000,
      };
      this.toasts.push(t);
      if (t.timeout > 0) {
        setTimeout(() => this.dismiss(id), t.timeout);
      }
      return id;
    },

    dismiss(id) {
      this.toasts = this.toasts.filter((t) => t.id !== id);
    },

    runToastAction(t) {
      if (t.onAction) t.onAction();
      this.dismiss(t.id);
    },

    openSheet(request) {
      this.sheetRequest = request;
    },

    closeSheet() {
      this.sheetRequest = null;
    },
  },
});
