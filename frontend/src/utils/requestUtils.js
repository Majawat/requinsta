// Design system: one colour per request state, everywhere (pill, filter chip,
// timeline dot, stat legend). The dot carries the state for colour-blind users;
// the label always ships too — never colour alone.
//
// pill = the class bundle for the rounded pill body; dot = the class for the
// leading dot. Colours map to the Foundations panel: amber / sky / emerald /
// rose / orange, all at the -400 dot / -300 text / /15 fill / /25 ring weights.
const STATUS = {
  PENDING:   { key: "PENDING",   label: "Pending",   pill: "bg-amber-400/15 text-amber-300 ring-1 ring-amber-400/25",     dot: "bg-amber-400" },
  APPROVED:  { key: "APPROVED",  label: "Approved",  pill: "bg-sky-400/15 text-sky-300 ring-1 ring-sky-400/25",           dot: "bg-sky-400" },
  FULFILLED: { key: "FULFILLED", label: "Available", pill: "bg-emerald-400/15 text-emerald-300 ring-1 ring-emerald-400/25", dot: "bg-emerald-400" },
  DENIED:    { key: "DENIED",    label: "Denied",    pill: "bg-rose-400/15 text-rose-300 ring-1 ring-rose-400/25",        dot: "bg-rose-400" },
  // Synthetic state: a fulfilled item that has an open issue needing a human.
  ISSUE:     { key: "ISSUE",     label: "Issue open", pill: "bg-orange-400/15 text-orange-300 ring-1 ring-orange-400/25", dot: "bg-orange-400" },
};

const STATUS_FALLBACK = {
  key: "OTHER",
  label: "Unknown",
  pill: "bg-slate-700/40 text-slate-300 ring-1 ring-slate-600/40",
  dot: "bg-slate-400",
};

export const statusMeta = (status) => STATUS[status] || STATUS_FALLBACK;

// Backwards-compatible helper (returns just the pill classes).
export const getStatusClasses = (status) => statusMeta(status).pill;

// Fixed ordering used by filter chips and the stat legend so a state is always
// in the same place.
export const STATUS_ORDER = ["PENDING", "APPROVED", "FULFILLED", "DENIED"];

// ---------------------------------------------------------------------------
// Media types — icon + word, no emoji. Each icon is inner-SVG markup rendered
// inside a <svg viewBox="0 0 24 24"> (see MediaIcon.vue). Colour identifies the
// type at a glance without competing with the status pills.
const MEDIA = {
  book:      { label: "Book",      cardLabel: "Books",      color: "#a78bfa", svg: '<path d="M5 4h13v16H6a1 1 0 0 1-1-1z"/><line x1="9" y1="4" x2="9" y2="20"/>' },
  audiobook: { label: "Audiobook", cardLabel: "Audiobooks", color: "#22d3ee", svg: '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><path d="M4 14h3v6H5a1 1 0 0 1-1-1z"/><path d="M20 14h-3v6h2a1 1 0 0 0 1-1z"/>' },
  music:     { label: "Music",     cardLabel: "Music",      color: "#f472b6", svg: '<circle cx="7" cy="18" r="3"/><circle cx="18" cy="16" r="3"/><path d="M10 18V6l11-2v12"/>' },
  movie:     { label: "Movie",     cardLabel: "Movies",     color: "#60a5fa", svg: '<rect x="3" y="4" width="18" height="16" rx="2"/><line x1="8" y1="4" x2="8" y2="20"/><line x1="16" y1="4" x2="16" y2="20"/>' },
  tv_show:   { label: "TV",        cardLabel: "TV shows",   color: "#2dd4bf", svg: '<rect x="3" y="7" width="18" height="13" rx="2"/><polyline points="8 3 12 7 16 3"/>' },
  comic:     { label: "Comic",     cardLabel: "Comics",     color: "#fbbf24", svg: '<path d="M12 7s-2-2-5-2H4v13h3c3 0 5 2 5 2s2-2 5-2h3V5h-3c-3 0-5 2-5 2z"/><line x1="12" y1="7" x2="12" y2="20"/>' },
  podcast:   { label: "Podcast",   cardLabel: "Podcasts",   color: "#a3e635", svg: '<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="8" y1="22" x2="16" y2="22"/>' },
  other:     { label: "Other",     cardLabel: "Other",      color: "#94a3b8", svg: '<rect x="4" y="4" width="16" height="16" rx="2"/><line x1="4" y1="10" x2="20" y2="10"/>' },
};

const MEDIA_FALLBACK = { label: "Media", cardLabel: "Media", color: "#94a3b8", svg: MEDIA.other.svg };

export const mediaIcon = (type) => MEDIA[type] || MEDIA_FALLBACK;
export const mediaTypeLabel = (type) => mediaIcon(type).label;

// Type-first picker cards (design frame A). Order is deliberate.
export const TYPE_CARDS = ["book", "audiobook", "music", "movie", "tv_show", "comic", "podcast"].map((value) => ({
  value,
  label: MEDIA[value].cardLabel,
  color: MEDIA[value].color,
}));

// ---------------------------------------------------------------------------
export const formatDate = (dateString) => {
  if (!dateString) return "Unknown";
  return new Date(dateString).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
};

// Relative time — "just now", "2 days ago", "3 weeks ago". Rows read as recency,
// not calendar dates.
export const formatRelative = (dateString) => {
  if (!dateString) return "";
  const then = new Date(dateString).getTime();
  if (Number.isNaN(then)) return "";
  const secs = Math.max(0, Math.round((Date.now() - then) / 1000));
  const table = [
    ["year", 31536000],
    ["month", 2592000],
    ["week", 604800],
    ["day", 86400],
    ["hour", 3600],
    ["minute", 60],
  ];
  for (const [unit, size] of table) {
    const n = Math.floor(secs / size);
    if (n >= 1) return `${n} ${unit}${n > 1 ? "s" : ""} ago`;
  }
  return "just now";
};

export const formatDateTime = (dateString) => {
  if (!dateString) return "";
  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
};
