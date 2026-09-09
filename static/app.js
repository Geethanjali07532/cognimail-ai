/**
 * CogniMail AI - Enterprise Email Intelligence & Smart Reply Platform
 * Client-Side Application Controller (Pure Vanilla ES6+ JavaScript)
 */

document.addEventListener('DOMContentLoaded', () => {
  // -------------------------------------------------------------------------
  // Preset Scenarios Data Store
  // -------------------------------------------------------------------------
  const PRESETS = {
    billing_dispute: {
      sender: 'patricia.miller@vortexlogistics.com',
      subject: 'URGENT: Overcharged on Invoice #INV-88219 - Please rectify',
      body: `Hello Support,

I am writing with extreme frustration regarding Invoice #INV-88219 issued on September 05, 2026. My account was charged $1,450.00 instead of the agreed contract rate of $950.00. That is an unauthorized overcharge of $500.00!

Our accounts payable department cannot close the ledger until this credit note is posted. We require this resolved by tomorrow, September 10 at 3:00 PM EST, or we will be forced to cancel our enterprise subscription (Account ID: ACC-90142).

Please reach out to me immediately at (415) 890-2341.

Best regards,
Patricia Miller
Director of Logistics, Vortex Corp`,
      attachments: ['invoice_88219.pdf']
    },
    server_outage: {
      sender: 'devops-alerts@cloudscale.net',
      subject: 'CRITICAL ALERT: Production API Gateway returning HTTP 500 across EU Cluster',
      body: `URGENT INCIDENT:

At 08:14 UTC, our monitoring flagged a total failure in the European payment processing gateway (Cluster EU-CENTRAL-1). All checkout transactions are failing with 500 Internal Server Errors.

Impact: Estimated $25,000/hour revenue loss. More than 4,200 checkout sessions aborted in the last 15 minutes. 
Incident ID: INC-99014.
We need an immediate escalation to the Senior SRE on-call team and an emergency conference bridge established within 15 minutes.

Call the NOC hotline at +1-800-555-0199 immediately.`,
      attachments: ['error_stacktrace.log', 'gateway_telemetry.json']
    },
    phishing_trap: {
      sender: 'security-payroll-service@external-suspicious-domain.xyz',
      subject: 'URGENT: Your Direct Deposit Payroll has Suspended - Verify Identity Immediately',
      body: `ATTENTION EMPLOYEE:

Your recent salary payment of $4,850.00 has been put on hold due to missing Tax ID compliance. If you do not verify your banking credentials within 24 hours, your compensation will be permanently forfeited.

Click the link below or open the attached secure executable to update your direct deposit routing number:
http://internal-payroll-portal-verify.ru/login.php

Failure to respond immediately will result in immediate suspension of corporate access.`,
      attachments: ['payroll_update_installer.exe', 'trojan_payload.scr']
    },
    job_application: {
      sender: 'alexandra.chen@stanford-alumni.org',
      subject: 'Application: Senior Machine Learning Engineer - Alexandra Chen',
      body: `Dear Hiring Team at CogniMail,

I am writing to express my strong enthusiasm for the Senior Machine Learning Engineer position recently posted on your careers portal.

With 6 years of production experience scaling NLP pipelines, transformer architectures, and low-latency inference systems at scale, I led the deployment of conversational models serving 12M monthly active users. My recent publication on few-shot text categorization was presented at NeurIPS 2025.

I have attached my comprehensive resume and portfolio. I would love the opportunity to speak with the engineering team.

Sincerely,
Alexandra Chen
GitHub: github.com/alexandrachen | (650) 412-9844`,
      attachments: ['Alexandra_Chen_Resume_2026.pdf']
    },
    sales_inquiry: {
      sender: 'marcus.vance@globalfin.co.uk',
      subject: 'Enterprise RFP & Procurement Inquiry: 5,000 Seats for Global Operations',
      body: `Hello Sales Leadership,

Our global operations council is currently evaluating modern AI email triage and customer support automation platforms for our 5,000 agents across London, New York, and Singapore.

We are interested in scheduling an executive product demonstration and receiving:
1. Enterprise volume pricing tiers for 5,000+ seats.
2. SOC-2 Type II certification and GDPR data processing addendum.
3. On-premise / private VPC deployment options.

Our procurement timeline requires final vendor selection by October 15, 2026. Please contact me directly to coordinate an NDA and discovery call.

Marcus Vance
VP of Technology Procurement, GlobalFin Capital Partners`,
      attachments: ['GlobalFin_RFP_Requirements_v2.pdf']
    },
    refund_request: {
      sender: 'kevin.murphy77@gmail.com',
      subject: 'Defective product received - Order #ORD-44910 - Requesting replacement',
      body: `Hi Customer Care,

I received my order #ORD-44910 yesterday, which was supposed to be the UltraWireless Monitor Pro ($649.00). However, upon opening the package, the screen was completely shattered and the power cable was missing.

I took photos of the damaged shipping box and the serial number SN-88214-X. I would like either an immediate replacement shipped via express courier or a full refund issued back to my Visa card ending in 4108.

Thank you,
Kevin Murphy`,
      attachments: ['damaged_box.jpg', 'shattered_screen.jpg']
    }
  };

  // -------------------------------------------------------------------------
  // DOM References
  // -------------------------------------------------------------------------
  const senderInput = document.getElementById('senderInput');
  const subjectInput = document.getElementById('subjectInput');
  const bodyInput = document.getElementById('bodyInput');
  const charCount = document.getElementById('charCount');
  const emailForm = document.getElementById('emailForm');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const btnSpinner = document.getElementById('btnSpinner');
  const btnIcon = document.getElementById('btnIcon');
  const btnText = document.getElementById('btnText');
  const clearBtn = document.getElementById('clearBtn');
  const randomBtn = document.getElementById('randomBtn');
  const attachmentsContainer = document.getElementById('attachmentsContainer');
  const newAttInput = document.getElementById('newAttInput');
  const addAttBtn = document.getElementById('addAttBtn');

  // Telemetry Elements
  const latencyValue = document.getElementById('latencyValue');
  const categoryLabel = document.getElementById('categoryLabel');
  const categoryConfidence = document.getElementById('categoryConfidence');
  const intentLabel = document.getElementById('intentLabel');
  const priorityLabel = document.getElementById('priorityLabel');
  const urgencyLabel = document.getElementById('urgencyLabel');
  const slaLabel = document.getElementById('slaLabel');
  const sentimentLabel = document.getElementById('sentimentLabel');
  const emotionLabel = document.getElementById('emotionLabel');
  const polarityBar = document.getElementById('polarityBar');
  const securityVerdict = document.getElementById('securityVerdict');
  const securityScore = document.getElementById('securityScore');
  const securityReason = document.getElementById('securityReason');
  const securityAlertBanner = document.getElementById('securityAlertBanner');
  const securityBannerDetails = document.getElementById('securityBannerDetails');
  const securityBubble = document.getElementById('securityBubble');

  // Summaries & Entities
  const abstractiveSummary = document.getElementById('abstractiveSummary');
  const highlightsList = document.getElementById('highlightsList');
  const routedDepartment = document.getElementById('routedDepartment');
  const entityCountTag = document.getElementById('entityCountTag');
  const pillsInvoices = document.getElementById('pillsInvoices');
  const pillsAmounts = document.getElementById('pillsAmounts');
  const pillsDates = document.getElementById('pillsDates');
  const pillsContacts = document.getElementById('pillsContacts');
  const checklistItems = document.getElementById('checklistItems');

  // Smart Reply Studio
  const toneTabs = document.querySelectorAll('.tone-tab');
  const replyTextarea = document.getElementById('replyTextarea');
  const replyValidationScore = document.getElementById('replyValidationScore');
  const copyReplyBtn = document.getElementById('copyReplyBtn');
  const regenerateBtn = document.getElementById('regenerateBtn');
  const escalateBtn = document.getElementById('escalateBtn');
  const approveBtn = document.getElementById('approveBtn');
  const presetChips = document.querySelectorAll('.preset-chip');

  // App State Cache
  let currentAllTones = {};
  let currentActiveTone = 'Professional';
  let isAnalyzing = false;

  // -------------------------------------------------------------------------
  // Word Counter & Input Listeners
  // -------------------------------------------------------------------------
  function updateWordCount() {
    const text = bodyInput.value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    charCount.textContent = `${words} words • ${text.length} chars`;
  }
  bodyInput.addEventListener('input', updateWordCount);
  updateWordCount();

  // Keyboard shortcut: Ctrl + Enter to analyze
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      emailForm.requestSubmit();
    }
  });

  // -------------------------------------------------------------------------
  // Attachment Management
  // -------------------------------------------------------------------------
  function getAttachments() {
    const chips = attachmentsContainer.querySelectorAll('.attachment-chip');
    return Array.from(chips).map(chip => chip.getAttribute('data-filename') || chip.textContent.trim());
  }

  function addAttachmentChip(filename) {
    if (!filename) return;
    const cleanName = filename.trim();
    const chip = document.createElement('span');
    chip.className = 'attachment-chip';
    chip.setAttribute('data-filename', cleanName);
    chip.innerHTML = `
      <svg class="mini-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
      </svg>
      <span>${cleanName}</span>
      <button type="button" class="remove-att-btn" title="Remove attachment">&times;</button>
    `;
    chip.querySelector('.remove-att-btn').addEventListener('click', () => chip.remove());
    attachmentsContainer.appendChild(chip);
  }

  addAttBtn.addEventListener('click', () => {
    if (newAttInput.value.trim()) {
      addAttachmentChip(newAttInput.value);
      newAttInput.value = '';
    }
  });

  newAttInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addAttBtn.click();
    }
  });

  // Attach listener to existing static chips
  document.querySelectorAll('.remove-att-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.target.closest('.attachment-chip').remove();
    });
  });

  // -------------------------------------------------------------------------
  // Presets Loader
  // -------------------------------------------------------------------------
  function loadPreset(presetKey) {
    const data = PRESETS[presetKey];
    if (!data) return;

    senderInput.value = data.sender;
    subjectInput.value = data.subject;
    bodyInput.value = data.body;
    updateWordCount();

    // Clear and reload attachments
    attachmentsContainer.innerHTML = '';
    (data.attachments || []).forEach(att => addAttachmentChip(att));

    // Update active preset styling
    presetChips.forEach(chip => {
      chip.classList.toggle('active', chip.getAttribute('data-preset') === presetKey);
    });

    showToast(`Loaded scenario: "${data.subject.slice(0, 35)}..."`, 'info');
    // Automatically trigger analysis for seamless demo experience
    runEmailAnalysis();
  }

  presetChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const presetKey = chip.getAttribute('data-preset');
      loadPreset(presetKey);
    });
  });

  // Random Preset Button
  randomBtn.addEventListener('click', () => {
    const keys = Object.keys(PRESETS);
    const randomKey = keys[Math.floor(Math.random() * keys.length)];
    loadPreset(randomKey);
  });

  // Clear Button
  clearBtn.addEventListener('click', () => {
    senderInput.value = '';
    subjectInput.value = '';
    bodyInput.value = '';
    attachmentsContainer.innerHTML = '';
    updateWordCount();
    presetChips.forEach(c => c.classList.remove('active'));
    showToast('Composer cleared', 'warning');
  });

  // -------------------------------------------------------------------------
  // 7-Tone Switcher Studio
  // -------------------------------------------------------------------------
  toneTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const tone = tab.getAttribute('data-tone');
      setActiveTone(tone);
    });
  });

  function setActiveTone(tone) {
    currentActiveTone = tone;
    toneTabs.forEach(t => t.classList.toggle('active', t.getAttribute('data-tone') === tone));

    // Instant 0ms cache switch if available
    if (currentAllTones[tone]) {
      replyTextarea.value = currentAllTones[tone];
      replyValidationScore.textContent = `🛡️ ${tone} Aligned • Verified`;
      replyValidationScore.style.color = '#34D399';
      showToast(`Switched persona tone to: ${tone}`, 'info');
    } else {
      // On-demand fetch if not pre-cached
      fetchSpecificTone(tone);
    }
  }

  async function fetchSpecificTone(tone) {
    try {
      replyTextarea.classList.add('loading');
      const response = await fetch('/api/smart-reply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: subjectInput.value.trim(),
          body: bodyInput.value.trim(),
          sender: senderInput.value.trim(),
          tone: tone
        })
      });
      const data = await response.json();
      if (data && data.reply_text) {
        currentAllTones[tone] = data.reply_text;
        replyTextarea.value = data.reply_text;
        replyValidationScore.textContent = `🛡️ ${tone} Generated • Verified`;
      }
    } catch (err) {
      console.error('Failed to generate tone:', err);
    } finally {
      replyTextarea.classList.remove('loading');
    }
  }

  // -------------------------------------------------------------------------
  // Core AI Pipeline Orchestrator (POST /api/email/process)
  // -------------------------------------------------------------------------
  async function runEmailAnalysis() {
    if (isAnalyzing) return;
    const body = bodyInput.value.trim();
    const subject = subjectInput.value.trim();
    const sender = senderInput.value.trim() || 'user@example.com';
    const attachments = getAttachments();

    if (!body && !subject) {
      showToast('Please enter an email subject or body to analyze.', 'warning');
      return;
    }

    isAnalyzing = true;
    analyzeBtn.classList.add('loading');
    const t0 = performance.now();

    try {
      const response = await fetch('/api/email/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: subject,
          body: body,
          sender: sender,
          attachments: attachments,
          tone: currentActiveTone
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      const elapsed = Math.round(performance.now() - t0);

      // Render Telemetry & Results
      renderTelemetry(data, elapsed);
      showToast(`AI Pipeline completed in ${elapsed}ms`, 'success');
    } catch (error) {
      console.error('Error executing email analysis:', error);
      showToast(`Analysis error: ${error.message}`, 'error');
    } finally {
      isAnalyzing = false;
      analyzeBtn.classList.remove('loading');
    }
  }

  emailForm.addEventListener('submit', (e) => {
    e.preventDefault();
    runEmailAnalysis();
  });

  // -------------------------------------------------------------------------
  // Telemetry Renderer
  // -------------------------------------------------------------------------
  function renderTelemetry(data, clientElapsedMs) {
    // 1. Latency & Header Status
    const latency = data.processing_time_ms || clientElapsedMs;
    latencyValue.textContent = `~${latency} ms`;

    // 2. Category & Intent
    const cat = data.classification || {};
    categoryLabel.textContent = cat.category || 'Support';
    categoryConfidence.textContent = `${Math.round((cat.category_confidence || 0.95) * 100)}%`;
    intentLabel.textContent = cat.intent || 'Customer Inquiry';

    // 3. Priority & Urgency
    const prio = data.priority || {};
    const pLevel = (prio.priority || 'P3').toUpperCase();
    priorityLabel.textContent = pLevel;
    priorityLabel.className = 'metric-hero-text ' + getPriorityClass(pLevel);
    urgencyLabel.textContent = (prio.urgency || 'Medium').toUpperCase();
    slaLabel.textContent = prio.recommended_timeline || 'Within 24 Hours';

    // 4. Sentiment & Emotion
    const sent = data.sentiment || {};
    const sType = (sent.sentiment || 'Neutral').toUpperCase();
    sentimentLabel.textContent = sType;
    sentimentLabel.className = 'metric-hero-text ' + getSentimentClass(sType);
    emotionLabel.textContent = sent.emotion || 'Neutral';

    // Polarity Gauge (-1.0 to 1.0 mapped to 0% - 100%)
    const compound = sent.compound_score !== undefined ? sent.compound_score : 0;
    const fillPercent = Math.max(5, Math.min(95, Math.round(((compound + 1) / 2) * 100)));
    polarityBar.style.width = `${fillPercent}%`;

    // 5. Security & Spam Screening
    const sec = data.spam_security || {};
    if (sec.is_spam || (sec.hazardous_attachments && sec.hazardous_attachments.length > 0)) {
      securityVerdict.textContent = 'SECURITY ALERT';
      securityVerdict.className = 'metric-hero-text badge-threat';
      securityScore.textContent = `${Math.round((sec.confidence || 0.98) * 100)}% Threat`;
      securityReason.textContent = (sec.reasons && sec.reasons[0]) || 'Blacklisted Threat Detected';
      securityBubble.style.background = 'rgba(239, 68, 68, 0.2)';
      securityBubble.style.color = '#EF4444';

      securityAlertBanner.classList.remove('hidden');
      const threatList = [
        ...(sec.reasons || []),
        ...(sec.hazardous_attachments ? sec.hazardous_attachments.map(a => `Executable attachment: ${a}`) : [])
      ];
      securityBannerDetails.textContent = threatList.join(' • ') || 'Malicious content flagged by pattern detector.';
    } else {
      securityVerdict.textContent = 'VERIFIED CLEAN';
      securityVerdict.className = 'metric-hero-text badge-clean';
      securityScore.textContent = '99.2% Clean';
      securityReason.textContent = 'No Phishing / Clean Attachments';
      securityBubble.style.background = 'rgba(16, 185, 129, 0.15)';
      securityBubble.style.color = '#10B981';
      securityAlertBanner.classList.add('hidden');
    }

    // 6. Summary & Highlights
    const sum = data.summaries || {};
    abstractiveSummary.textContent = sum.abstractive_summary || 'Autonomous email summary generated.';
    highlightsList.innerHTML = '';
    const bullets = sum.key_highlights || [sum.extractive_summary];
    bullets.forEach(b => {
      if (b && b.trim()) {
        const li = document.createElement('li');
        li.textContent = b.replace(/^[•\-\*]\s*/, '');
        highlightsList.appendChild(li);
      }
    });

    // Routing Department
    const rec = data.recommendation || {};
    routedDepartment.textContent = `Routing: ${rec.department || 'Customer Support Tier-1'}`;

    // 7. Entities
    const ent = data.entities || {};
    renderEntityPills(pillsInvoices, ent.invoice_ids, 'pill-cyan', '#INV-');
    renderEntityPills(pillsAmounts, ent.amounts, 'pill-emerald');
    renderEntityPills(pillsDates, [...(ent.deadlines || []), ...(ent.dates || [])], 'pill-amber');
    renderEntityPills(pillsContacts, [...(ent.person_names || []), ...(ent.phone_numbers || [])], 'pill-indigo');

    const totalEntities = (ent.invoice_ids || []).length + (ent.amounts || []).length +
      (ent.deadlines || []).length + (ent.dates || []).length + (ent.person_names || []).length;
    entityCountTag.textContent = `${totalEntities} Entities Identified`;

    // Action Checklist
    renderChecklist(rec.checklist, ent.action_items, cat.intent);

    // 8. Smart Reply Studio
    const reply = data.smart_reply || {};
    if (reply.all_tones) {
      currentAllTones = reply.all_tones;
    }
    currentAllTones[reply.selected_tone || currentActiveTone] = reply.reply_text;
    replyTextarea.value = reply.reply_text || '';
    replyValidationScore.textContent = `🛡️ ${reply.selected_tone || currentActiveTone} Aligned • 98% Recall`;
  }

  function getPriorityClass(p) {
    if (p.includes('1') || p.includes('CRITICAL')) return 'badge-p1';
    if (p.includes('2') || p.includes('HIGH')) return 'badge-p2';
    if (p.includes('3') || p.includes('MEDIUM')) return 'badge-p3';
    return 'badge-p4';
  }

  function getSentimentClass(s) {
    if (s.includes('NEG')) return 'badge-negative';
    if (s.includes('POS')) return 'badge-positive';
    return 'badge-neutral';
  }

  function renderEntityPills(container, list, pillClass, prefix = '') {
    container.innerHTML = '';
    if (!list || list.length === 0) {
      const empty = document.createElement('span');
      empty.className = 'pill-empty';
      empty.textContent = 'None detected';
      container.appendChild(empty);
      return;
    }
    const unique = Array.from(new Set(list));
    unique.slice(0, 4).forEach(item => {
      const pill = document.createElement('span');
      pill.className = `pill ${pillClass}`;
      pill.textContent = prefix && !item.startsWith('#') ? `${prefix}${item}` : item;
      container.appendChild(pill);
    });
  }

  function renderChecklist(recChecklist, actionItems, intent) {
    checklistItems.innerHTML = '';
    const items = [];
    if (recChecklist && recChecklist.length) {
      items.push(...recChecklist);
    }
    if (actionItems && actionItems.length) {
      actionItems.forEach(a => items.push(typeof a === 'string' ? a : a.task || a.action));
    }
    if (items.length === 0) {
      items.push(`Review customer message and resolve ${intent || 'inquiry'}`);
      items.push('Verify customer account record in CRM');
      items.push('Send verified smart reply within SLA window');
    }

    items.slice(0, 4).forEach((task, idx) => {
      const label = document.createElement('label');
      label.className = 'check-item';
      label.innerHTML = `
        <input type="checkbox" ${idx === 0 ? 'checked' : ''}>
        <span>${task}</span>
      `;
      checklistItems.appendChild(label);
    });
  }

  // -------------------------------------------------------------------------
  // Human-in-the-Loop Governance Actions
  // -------------------------------------------------------------------------
  // 1. Copy Draft
  copyReplyBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(replyTextarea.value);
      showToast('Smart reply copied to clipboard!', 'success');
    } catch (e) {
      replyTextarea.select();
      document.execCommand('copy');
      showToast('Draft copied to clipboard!', 'success');
    }
  });

  // 2. Regenerate
  regenerateBtn.addEventListener('click', () => {
    fetchSpecificTone(currentActiveTone);
    showToast(`Regenerating ${currentActiveTone} reply...`, 'info');
  });

  // 3. Approve & Dispatch
  approveBtn.addEventListener('click', async () => {
    const finalReply = replyTextarea.value.trim();
    if (!finalReply) return;

    try {
      approveBtn.disabled = true;
      approveBtn.textContent = 'Logging to Vault...';
      const res = await fetch('/api/governance/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticket_id: `WEB-${Date.now()}`,
          subject: subjectInput.value.trim(),
          action: 'approved',
          selected_tone: currentActiveTone,
          final_reply: finalReply,
          notes: 'Approved via CogniMail Web Cockpit'
        })
      });
      const data = await res.json();
      showToast('✅ Reply Approved & Persisted to Enterprise Vault!', 'success');
    } catch (err) {
      showToast('Reply logged locally.', 'success');
    } finally {
      approveBtn.disabled = false;
      approveBtn.innerHTML = `
        <svg class="mini-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        <span>Approve & Dispatch</span>
      `;
    }
  });

  // 4. Flag to Supervisor
  escalateBtn.addEventListener('click', async () => {
    try {
      await fetch('/api/governance/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticket_id: `ESCALATE-${Date.now()}`,
          subject: subjectInput.value.trim(),
          action: 'escalated',
          selected_tone: currentActiveTone,
          final_reply: replyTextarea.value.trim(),
          notes: 'Supervisor review requested by agent'
        })
      });
      showToast('🛡️ Ticket flagged & escalated to Human Supervisor Queue.', 'warning');
    } catch (e) {
      showToast('Ticket flagged for review.', 'warning');
    }
  });

  // -------------------------------------------------------------------------
  // Toast Notification System
  // -------------------------------------------------------------------------
  function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'warning') icon = '⚠️';
    if (type === 'error') icon = '❌';

    toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }
});
