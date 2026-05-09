// Partner Network Phase 1 — shared config & helpers.
// Loaded by photodesk.html and client.html.

window.PartnerNetwork = (function () {
  // Hardcoded UID Эдмонта-в-проде (legacy admin до миграции).
  // Получить: Firebase Console → Authentication → Users → найти edmont.nadlan@gmail.com → Copy UID.
  // ВНИМАНИЕ: после миграции (когда users/{edmont-uid} существует) этот fallback не сработает.
  const LEGACY_ADMIN_UIDS = ['aJJ6ifCCNSgdpEigzunjw6Fp3Gv1'];

  const PUBLIC_STATUS_MAP = {
    'pending':                   'received',
    'approved':                  'scheduled',
    'ממתין לאישור':              'received',
    'מתוכנן':                    'scheduled',
    'צולם':                      'in_progress',
    'בעיבוד':                    'in_progress',
    'ממתין למסירה':              'in_progress',
    'נמסר':                      'delivered',
    'confirmed':                 'scheduled',
    'in_flight':                 'in_progress',
    'processing':                'in_progress',
    'delivered':                 'delivered',
    'cancelled':                 'cancelled',
    'rejected':                  'cancelled'
  };

  function isFinalStatus(order) {
    if (!order || !order.status) return false;
    if (order.status === 'cancelled' || order.status === 'rejected') return true;
    if ((order.status === 'נמסר' || order.status === 'delivered') && order.receiptSent === true) return true;
    return false;
  }

  function partnerNetworkEnabled(store) {
    return Boolean(store && store.data && store.data.partnerNetworkEnabled === true);
  }

  function isLegacyAdmin(uid) { return LEGACY_ADMIN_UIDS.includes(uid); }
  function mapStatusToPublic(status) { return PUBLIC_STATUS_MAP[status] || 'in_progress'; }

  function randomToken() {
    const arr = new Uint8Array(16);
    crypto.getRandomValues(arr);
    return Array.from(arr).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  return {
    LEGACY_ADMIN_UIDS, PUBLIC_STATUS_MAP,
    isFinalStatus, partnerNetworkEnabled, isLegacyAdmin,
    mapStatusToPublic, randomToken
  };
})();
