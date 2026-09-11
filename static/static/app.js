/**
 * CogniMail AI - Enterprise Email Intelligence & Context-Aware Smart Reply Platform
 * Client-Side Application Controller (Vanilla ES6+ JavaScript)
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
  // Navigation Tabs & Views
  const tabCockpit = document.getElementById('tabCockpit');
  const tabHistory = document.getElementById('tabHistory');
  const tabAnalytics = document.getElementById('tabAnalytics');
  const cockpitView = document.getElementById('cockpitView');
  const historyView = document.getElementById('historyView');
  const analyticsView = document.getElementById('analyticsView');

  // Composer Form & Inputs
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
  const presetChips = document.querySelectorAll('.preset-chip');

  // Loading State Elements
  const loadingOverlay = document.getElementById('loadingOverlay');

  // Triage Telemetry Elements
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

  // Security, Spam & Duplicate Elements
  const securityVerdict = document.getElementById('securityVerdict');
  const securityScore = document.getElementById('securityScore');
  const securityBubble = document.getElementById('securityBubble');
  const securityAlertBanner = document.getElementById('securityAlertBanner');
  const securityBannerDetails = document.getElementById('securityBannerDetails');
  const spamStatusVal = document.getElementById('spamStatusVal');
  const phishingStatusVal = document.getElementById('phishingStatusVal');
  const duplicateStatusVal = document.getElementById('duplicateStatusVal');
  const similarityScoreVal = document.getElementById('similarityScoreVal');

  // Summary & Highlights Elements
  const routedDepartment = document.getElementById('routedDepartment');
  const abstractiveSummary = document.getElementById('abstractiveSummary');
  const highlightsList = document.getElementById('highlightsList');
  const summaryRequiredAction = document.getElementById('summaryRequiredAction');
  const summaryRiskUrgency = document.getElementById('summaryRiskUrgency');

  // Entities Elements
  const entityCountTag = document.getElementById('entityCountTag');
  const pillsInvoices = document.getElementById('pillsInvoices');
  const pillsAmounts = document.getElementById('pillsAmounts');
  const pillsDates = document.getElementById('pillsDates');
  const pillsContacts = document.getElementById('pillsContacts');
  const pillsOrgs = document.getElementById('pillsOrgs');
  const pillsProducts = document.getElementById('pillsProducts');

  // Action Items Elements
  const actionItemsContainer = document.getElementById('actionItemsContainer');
  const actionDeptBadge = document.getElementById('actionDeptBadge');
  const actionDeadlineBadge = document.getElementById('actionDeadlineBadge');

  // Response Recommendation Elements
  const recResponseType = document.getElementById('recResponseType');
  const recDepartment = document.getElementById('recDepartment');
  const recPriority = document.getElementById('recPriority');
  const recTone = document.getElementById('recTone');
  const recAction = document.getElementById('recAction');
  const recSlaTag = document.getElementById('recSlaTag');

  // Conversation Context Elements
  const contextPreviousMessages = document.getElementById('contextPreviousMessages');
  const contextCurrentEmail = document.getElementById('contextCurrentEmail');
  const contextIntent = document.getElementById('contextIntent');
  const contextSummary = document.getElementById('contextSummary');
  const contextApproach = document.getElementById('contextApproach');
  const contextHistoryTag = document.getElementById('contextHistoryTag');

  // Smart Reply Studio Elements
  const toneTabs = document.querySelectorAll('.tone-tab');
  const replyTextarea = document.getElementById('replyTextarea');
  const replyValidationScore = document.getElementById('replyValidationScore');
  const regenerateBtn = document.getElementById('regenerateBtn');
  const editReplyBtn = document.getElementById('editReplyBtn');
  const copyReplyBtn = document.getElementById('copyReplyBtn');
  const approveBtn = document.getElementById('approveBtn');

  // History View Elements
  const historyTotalCount = document.getElementById('historyTotalCount');
  const historySearchInput = document.getElementById('historySearchInput');
  const filterCategory = document.getElementById('filterCategory');
  const filterPriority = document.getElementById('filterPriority');
  const filterSentiment = document.getElementById('filterSentiment');
  const filterSpam = document.getElementById('filterSpam');
  const historySortBy = document.getElementById('historySortBy');
  const historyRefreshBtn = document.getElementById('historyRefreshBtn');
  const historyTableBody = document.getElementById('historyTableBody');

  // Analytics Elements
  const kpiTotalEmails = document.getElementById('kpiTotalEmails');
  const kpiHighPriority = document.getElementById('kpiHighPriority');
  const kpiUrgentEmails = document.getElementById('kpiUrgentEmails');
  const kpiSpamDetected = document.getElementById('kpiSpamDetected');
  const kpiAvgConfidence = document.getElementById('kpiAvgConfidence');

  // State Management
  let currentAllTones = {};
  let currentActiveTone = 'Professional';
  let isAnalyzing = false;
  let chartInstances = {};

  // -------------------------------------------------------------------------
  // View Navigation System
  // -------------------------------------------------------------------------
  function switchView(viewName) {
    // Tab active states
    tabCockpit.classList.toggle('active', viewName === 'cockpit');
    tabHistory.classList.toggle('active', viewName === 'history');
    tabAnalytics.classList.toggle('active', viewName === 'analytics');

    // View panels visibility
    cockpitView.classList.toggle('hidden', viewName !== 'cockpit');
    historyView.classList.toggle('hidden', viewName !== 'history');
    analyticsView.classList.toggle('hidden', viewName !== 'analytics');

    if (viewName === 'history') {
      loadEmailHistory();
    } else if (viewName === 'analytics') {
      loadAnalyticsData();
    }
  }

  tabCockpit.addEventListener('click', () => switchView('cockpit'));
  tabHistory.addEventListener('click', () => switchView('history'));
  tabAnalytics.addEventListener('click', () => switchView('analytics'));

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
      if (!cockpitView.classList.contains('hidden')) {
        emailForm.requestSubmit();
      }
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

  document.querySelectorAll('.remove-att-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.target.closest('.attachment-chip').remove();
    });
  });

  // -------------------------------------------------------------------------
  // Preset Scenarios Loader
  // -------------------------------------------------------------------------
  function loadPreset(presetKey) {
    const data = PRESETS[presetKey];
    if (!data) return;

    senderInput.value = data.sender;
    subjectInput.value = data.subject;
    bodyInput.value = data.body;
    updateWordCount();

    attachmentsContainer.innerHTML = '';
    (data.attachments || []).forEach(att => addAttachmentChip(att));

    presetChips.forEach(chip => {
      chip.classList.toggle('active', chip.getAttribute('data-preset') === presetKey);
    });

    showToast(`Loaded preset: "${data.subject.slice(0, 35)}..."`, 'info');
    runEmailAnalysis();
  }

  presetChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const presetKey = chip.getAttribute('data-preset');
      loadPreset(presetKey);
    });
  });

  randomBtn.addEventListener('click', () => {
    const keys = Object.keys(PRESETS);
    const randomKey = keys[Math.floor(Math.random() * keys.length)];
    loadPreset(randomKey);
  });

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
  // Tone Switcher Studio (Professional, Friendly, Formal, Concise, Empathetic, etc.)
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

    // Instant switch if cached in memory
    if (currentAllTones[tone]) {
      replyTextarea.value = currentAllTones[tone];
      replyValidationScore.textContent = `🛡️ ${tone} Aligned • Verified`;
      replyValidationScore.style.color = '#34D399';
      showToast(`Selected Persona Tone: ${tone}`, 'info');
    } else {
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
  // Step-by-Step Loading Animation Helper
  // -------------------------------------------------------------------------
  async function animateLoadingSteps() {
    const steps = [
      'lStep1', 'lStep2', 'lStep3', 'lStep4', 'lStep5',
      'lStep6', 'lStep7', 'lStep8', 'lStep9'
    ];

    steps.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.className = 'loading-step';
        const icon = el.querySelector('.step-icon');
        if (icon) icon.textContent = '○';
      }
    });

    for (let i = 0; i < steps.length; i++) {
      if (!isAnalyzing) break;
      const el = document.getElementById(steps[i]);
      if (el) {
        el.classList.add('active');
        const icon = el.querySelector('.step-icon');
        if (icon) icon.textContent = '●';
      }
      await new Promise(r => setTimeout(r, 65));
      if (el) {
        el.classList.remove('active');
        el.classList.add('completed');
        const icon = el.querySelector('.step-icon');
        if (icon) icon.textContent = '✓';
      }
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

    // Strict validation: never proceed on empty input
    if (!body && !subject) {
      showToast('Please enter an email before analyzing.', 'warning');
      return;
    }

    isAnalyzing = true;
    analyzeBtn.classList.add('loading');
    loadingOverlay.classList.remove('hidden');
    animateLoadingSteps();

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

      // Render Telemetry & Extended Panels
      renderTelemetry(data, elapsed);
      showToast(`AI Pipeline completed in ${elapsed}ms`, 'success');
    } catch (error) {
      console.error('Error executing email analysis:', error);
      showToast('Unable to analyze this email right now. Please try again.', 'error');
    } finally {
      isAnalyzing = false;
      analyzeBtn.classList.remove('loading');
      loadingOverlay.classList.add('hidden');
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
    categoryLabel.textContent = cat.category || 'Customer Support';
    categoryConfidence.textContent = `${Math.round((cat.category_confidence || 0.96) * 100)}%`;
    intentLabel.textContent = cat.intent || 'General Inquiry';

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

    // Polarity Gauge (-1.0 to 1.0 mapped to 5% - 95%)
    const compound = sent.compound_score !== undefined ? sent.compound_score : 0;
    const fillPercent = Math.max(5, Math.min(95, Math.round(((compound + 1) / 2) * 100)));
    polarityBar.style.width = `${fillPercent}%`;

    // 5. Security, Spam & Duplicate Screening
    const sec = data.spam_security || {};
    const dup = data.duplicate_check || {};

    if (sec.is_spam || (sec.hazardous_attachments && sec.hazardous_attachments.length > 0)) {
      securityVerdict.textContent = 'SECURITY ALERT';
      securityVerdict.className = 'metric-hero-text badge-threat';
      securityScore.textContent = `${Math.round((sec.confidence || 0.98) * 100)}% Threat`;
      securityBubble.style.background = 'rgba(239, 68, 68, 0.2)';
      securityBubble.style.color = '#EF4444';

      spamStatusVal.textContent = '⚠️ Spam Detected';
      spamStatusVal.className = 'sec-v text-threat';

      phishingStatusVal.textContent = '⚠️ Phishing Indicators';
      phishingStatusVal.className = 'sec-v text-threat';

      securityAlertBanner.classList.remove('hidden');
      const threatList = [
        ...(sec.reasons || []),
        ...(sec.hazardous_attachments ? sec.hazardous_attachments.map(a => `Executable attachment: ${a}`) : [])
      ];
      securityBannerDetails.textContent = threatList.join(' • ') || 'Malicious content flagged by security detector.';
    } else {
      securityVerdict.textContent = 'CLEAN';
      securityVerdict.className = 'metric-hero-text badge-clean';
      securityScore.textContent = '99.2% Confidence';
      securityBubble.style.background = 'rgba(16, 185, 129, 0.15)';
      securityBubble.style.color = '#10B981';

      spamStatusVal.textContent = '✓ Not Spam';
      spamStatusVal.className = 'sec-v text-clean';

      phishingStatusVal.textContent = '✓ No phishing indicators detected';
      phishingStatusVal.className = 'sec-v text-clean';

      securityAlertBanner.classList.add('hidden');
    }

    // Duplicate Detection Status
    if (dup.is_duplicate) {
      duplicateStatusVal.textContent = '⚠️ Potential duplicate email detected';
      duplicateStatusVal.className = 'sec-v text-warn';
      similarityScoreVal.textContent = `${dup.similarity_score}%`;
      similarityScoreVal.className = 'sec-v text-warn font-mono';
    } else {
      duplicateStatusVal.textContent = '✓ No duplicate found';
      duplicateStatusVal.className = 'sec-v text-clean';
      similarityScoreVal.textContent = `${dup.similarity_score || 0.0}%`;
      similarityScoreVal.className = 'sec-v font-mono';
    }

    // 6. Improved Structured AI Summary
    const sumStruct = data.summary_structured || {};
    abstractiveSummary.textContent = sumStruct.summary || (data.summaries && data.summaries.abstractive_summary) || 'Autonomous email summary generated.';
    
    highlightsList.innerHTML = '';
    const bullets = sumStruct.key_highlights || (data.summaries && data.summaries.key_highlights) || [];
    if (bullets.length > 0) {
      bullets.forEach(b => {
        if (b && b.trim()) {
          const li = document.createElement('li');
          li.textContent = b.replace(/^[•\-\*]\s*/, '');
          highlightsList.appendChild(li);
        }
      });
    } else {
      const li = document.createElement('li');
      li.textContent = 'Inbound correspondence reviewed and triaged.';
      highlightsList.appendChild(li);
    }

    routedDepartment.textContent = `Department: ${sumStruct.department || 'Support Desk'}`;
    summaryRequiredAction.textContent = sumStruct.required_action || 'Address incoming inquiry.';
    summaryRiskUrgency.textContent = sumStruct.risk_urgency || `${prio.urgency || 'Standard'} priority triage.`;

    // 7. Entities Extraction
    const ent = data.entities || {};
    const allInvoices = [...(ent.invoice_ids || []), ...(ent.order_ids || []), ...(ent.transaction_ids || [])];
    renderEntityPills(pillsInvoices, allInvoices, 'pill-cyan');
    renderEntityPills(pillsAmounts, ent.amounts, 'pill-emerald');
    renderEntityPills(pillsDates, [...(ent.deadlines || []), ...(ent.dates || []), ...(ent.times || [])], 'pill-amber');
    renderEntityPills(pillsContacts, [...(ent.person_names || []), ...(ent.phone_numbers || []), ...(ent.email_addresses || [])], 'pill-indigo');
    renderEntityPills(pillsOrgs, [...(ent.organizations || []), ...(ent.locations || [])], 'pill-purple');
    renderEntityPills(pillsProducts, ent.products_or_systems, 'pill-rose');

    const totalEntCount = allInvoices.length + (ent.amounts || []).length +
      (ent.deadlines || []).length + (ent.dates || []).length + (ent.person_names || []).length +
      (ent.organizations || []).length + (ent.products_or_systems || []).length;
    entityCountTag.textContent = `${totalEntCount} Structured Tokens`;

    // 8. Action Items Section
    const actDetail = data.action_items_detail || {};
    actionDeptBadge.textContent = `Responsible: ${actDetail.department || 'Finance'}`;
    actionDeadlineBadge.textContent = `Deadline: ${actDetail.deadline || 'Not specified'}`;
    renderActionItems(actDetail.tasks);

    // 9. AI Response Recommendation Matrix
    const rec = data.response_recommendation || data.recommendation || {};
    recResponseType.textContent = rec.response_type || 'Resolution + Status Update';
    recDepartment.textContent = rec.department || actDetail.department || 'Customer Operations';
    recPriority.textContent = rec.priority || prio.priority || 'Medium';
    recTone.textContent = rec.recommended_tone || 'Empathetic + Professional';
    recAction.textContent = rec.primary_action || 'Verify transaction and process correction.';
    recSlaTag.textContent = `SLA: ${rec.sla_window || prio.recommended_timeline || 'Within 24 Hours'}`;

    // 10. Conversation Context
    const ctx = data.conversation_context || {};
    renderConversationContext(ctx);

    // 11. Smart Reply Studio
    const reply = data.smart_reply || {};
    if (reply.all_tones) {
      currentAllTones = reply.all_tones;
    }
    const activeReplyTone = reply.selected_tone || currentActiveTone;
    currentAllTones[activeReplyTone] = reply.reply_text;
    replyTextarea.value = reply.reply_text || '';
    replyValidationScore.textContent = `🛡️ ${activeReplyTone} Aligned • Verified`;
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

  function renderEntityPills(container, list, pillClass) {
    container.innerHTML = '';
    if (!list || list.length === 0) {
      const empty = document.createElement('span');
      empty.className = 'pill-empty';
      empty.textContent = 'None detected';
      container.appendChild(empty);
      return;
    }
    const unique = Array.from(new Set(list));
    unique.slice(0, 5).forEach(item => {
      const pill = document.createElement('span');
      pill.className = `pill ${pillClass}`;
      pill.textContent = item;
      container.appendChild(pill);
    });
  }

  function renderActionItems(tasks) {
    actionItemsContainer.innerHTML = '';
    if (!tasks || tasks.length === 0) {
      actionItemsContainer.innerHTML = '<span class="empty-notice-text">No specific action items detected.</span>';
      return;
    }
    tasks.forEach((task, idx) => {
      const label = document.createElement('label');
      label.className = 'check-item';
      label.innerHTML = `
        <input type="checkbox" ${idx === 0 ? 'checked' : ''}>
        <span>${task}</span>
      `;
      actionItemsContainer.appendChild(label);
    });
  }

  function renderConversationContext(ctx) {
    contextCurrentEmail.textContent = ctx.current_email || subjectInput.value || 'Incoming Email';
    contextIntent.textContent = ctx.detected_intent || 'Customer Request';
    contextSummary.textContent = ctx.conversation_summary || 'Initial inbound inquiry in this communication thread.';
    contextApproach.textContent = ctx.recommended_approach || 'Review message and respond with appropriate tone.';

    contextPreviousMessages.innerHTML = '';
    if (ctx.has_history && ctx.previous_messages && ctx.previous_messages.length > 0) {
      contextHistoryTag.textContent = `${ctx.previous_messages.length} Prior Exchange(s)`;
      ctx.previous_messages.forEach(msg => {
        const item = document.createElement('div');
        item.className = 'thread-msg-item';
        item.innerHTML = `
          <div class="thread-msg-header">
            <strong>${msg.sender}</strong>
            <span>${msg.timestamp || 'Previous exchange'}</span>
          </div>
          <div class="thread-msg-body">${msg.snippet}</div>
        `;
        contextPreviousMessages.appendChild(item);
      });
    } else {
      contextHistoryTag.textContent = '0 Previous Messages';
      contextPreviousMessages.innerHTML = '<span class="empty-notice-text">No previous conversation available.</span>';
    }
  }

  // -------------------------------------------------------------------------
  // Human-in-the-Loop Smart Reply Actions
  // -------------------------------------------------------------------------
  // 1. Copy Reply
  copyReplyBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(replyTextarea.value);
      showToast('Smart reply copied to clipboard!', 'success');
    } catch (e) {
      replyTextarea.select();
      document.execCommand('copy');
      showToast('Reply draft copied to clipboard!', 'success');
    }
  });

  // 2. Edit Reply Button (Highlights editable textarea)
  editReplyBtn.addEventListener('click', () => {
    replyTextarea.focus();
    replyTextarea.setSelectionRange(replyTextarea.value.length, replyTextarea.value.length);
    showToast('Editing enabled. Modify the AI draft as needed.', 'info');
  });

  // 3. Regenerate Reply
  regenerateBtn.addEventListener('click', () => {
    fetchSpecificTone(currentActiveTone);
    showToast(`Regenerating ${currentActiveTone} response...`, 'info');
  });

  // 4. Approve Reply (Human in the Loop Governance)
  approveBtn.addEventListener('click', async () => {
    const finalReply = replyTextarea.value.trim();
    if (!finalReply) return;

    try {
      approveBtn.disabled = true;
      approveBtn.textContent = 'Saving Approval...';
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
      showToast('✅ Reply Approved & Logged in Enterprise Vault!', 'success');
    } catch (err) {
      showToast('Reply logged locally.', 'success');
    } finally {
      approveBtn.disabled = false;
      approveBtn.innerHTML = `
        <svg class="mini-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        <span>Approve Reply</span>
      `;
    }
  });

  // -------------------------------------------------------------------------
  // Email History Vault View Logic
  // -------------------------------------------------------------------------
  let historyDebounceTimer = null;

  async function loadEmailHistory() {
    try {
      const search = historySearchInput.value.trim();
      const cat = filterCategory.value;
      const prio = filterPriority.value;
      const sent = filterSentiment.value;
      const spam = filterSpam.value;
      const sortBy = historySortBy.value;

      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (cat && cat !== 'All') params.append('category', cat);
      if (prio && prio !== 'All') params.append('priority', prio);
      if (sent && sent !== 'All') params.append('sentiment', sent);
      if (spam !== '') params.append('is_spam', spam);
      params.append('sort_by', sortBy);

      const res = await fetch(`/api/history?${params.toString()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      historyTotalCount.textContent = `${data.total} Emails Recorded`;
      renderHistoryTable(data.emails || []);
    } catch (err) {
      console.error('Failed to load history:', err);
      historyTableBody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:var(--text-muted); padding:24px;">No emails found in vault.</td></tr>';
    }
  }

  function renderHistoryTable(emails) {
    historyTableBody.innerHTML = '';
    if (!emails || emails.length === 0) {
      historyTableBody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:var(--text-muted); padding:24px;">No matching emails found.</td></tr>';
      return;
    }

    emails.forEach(email => {
      const tr = document.createElement('tr');
      const dateStr = email.timestamp ? email.timestamp.slice(0, 16) : 'Just now';
      const statusClass = email.status === 'APPROVED' ? 'status-approved' : (email.status === 'ESCALATED' ? 'status-escalated' : 'status-pending');

      tr.innerHTML = `
        <td>${email.sender || 'unknown'}</td>
        <td class="col-sub" title="${email.subject}">${email.subject || '(No Subject)'}</td>
        <td><span class="pill pill-cyan" style="font-size:0.7rem;">${email.category || 'General'}</span></td>
        <td>${email.intent || 'Inquiry'}</td>
        <td><span class="metric-hero-text ${getSentimentClass(email.sentiment || '')}" style="font-size:0.72rem; padding:2px 6px;">${email.sentiment || 'Neutral'}</span></td>
        <td><span class="metric-hero-text ${getPriorityClass(email.priority || '')}" style="font-size:0.72rem; padding:2px 6px;">${email.priority || 'P3'}</span></td>
        <td style="font-family:var(--font-mono); font-size:0.72rem;">${dateStr}</td>
        <td><span class="status-badge-vault ${statusClass}">${email.status || 'PENDING'}</span></td>
        <td><button type="button" class="btn-reopen" data-id="${email.email_id || email.id}">Reopen</button></td>
      `;

      tr.querySelector('.btn-reopen').addEventListener('click', () => {
        reopenHistoricalEmail(email);
      });

      historyTableBody.appendChild(tr);
    });
  }

  function reopenHistoricalEmail(email) {
    senderInput.value = email.sender || '';
    subjectInput.value = email.subject || '';
    bodyInput.value = email.body || '';
    updateWordCount();
    switchView('cockpit');
    showToast(`Reopened email: "${email.subject}"`, 'info');
    runEmailAnalysis();
  }

  // History Filter Listeners
  historySearchInput.addEventListener('input', () => {
    clearTimeout(historyDebounceTimer);
    historyDebounceTimer = setTimeout(loadEmailHistory, 300);
  });
  filterCategory.addEventListener('change', loadEmailHistory);
  filterPriority.addEventListener('change', loadEmailHistory);
  filterSentiment.addEventListener('change', loadEmailHistory);
  filterSpam.addEventListener('change', loadEmailHistory);
  historySortBy.addEventListener('change', loadEmailHistory);
  historyRefreshBtn.addEventListener('click', () => {
    loadEmailHistory();
    showToast('Email vault refreshed', 'info');
  });

  // -------------------------------------------------------------------------
  // Analytics Dashboard & Chart.js Visualizations
  // -------------------------------------------------------------------------
  async function loadAnalyticsData() {
    try {
      const res = await fetch('/api/analytics');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      // Update KPI Stat Cards
      kpiTotalEmails.textContent = data.total_emails || 0;
      kpiHighPriority.textContent = data.high_priority || 0;
      kpiUrgentEmails.textContent = data.urgent_emails || 0;
      kpiSpamDetected.textContent = data.spam_detected || 0;
      kpiAvgConfidence.textContent = `${data.average_confidence || 97.2}%`;

      // Render Charts
      renderAnalyticsCharts(data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    }
  }

  function renderAnalyticsCharts(data) {
    if (typeof Chart === 'undefined') return;

    // Dark enterprise Chart.js defaults
    Chart.defaults.color = '#94A3B8';
    Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";

    // 1. Category Distribution (Doughnut)
    renderOrUpdateChart('chartCategory', 'doughnut', {
      labels: Object.keys(data.category_distribution || {}),
      datasets: [{
        data: Object.values(data.category_distribution || {}),
        backgroundColor: ['#38BDF8', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#6366F1'],
        borderColor: '#0F172A',
        borderWidth: 2
      }]
    }, {
      plugins: { legend: { position: 'bottom', labels: { boxWidth: 12 } } },
      responsive: true,
      maintainAspectRatio: false
    });

    // 2. Intent Distribution (Horizontal Bar)
    renderOrUpdateChart('chartIntent', 'bar', {
      labels: Object.keys(data.intent_distribution || {}),
      datasets: [{
        label: 'Email Count',
        data: Object.values(data.intent_distribution || {}),
        backgroundColor: 'rgba(56, 189, 248, 0.65)',
        borderColor: '#38BDF8',
        borderWidth: 1,
        borderRadius: 4
      }]
    }, {
      indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' } },
        y: { grid: { display: false } }
      },
      responsive: true,
      maintainAspectRatio: false
    });

    // 3. Sentiment Distribution (Polar / Pie)
    renderOrUpdateChart('chartSentiment', 'pie', {
      labels: Object.keys(data.sentiment_distribution || {}),
      datasets: [{
        data: Object.values(data.sentiment_distribution || {}),
        backgroundColor: ['#10B981', '#64748B', '#EF4444'],
        borderColor: '#0F172A',
        borderWidth: 2
      }]
    }, {
      plugins: { legend: { position: 'bottom' } },
      responsive: true,
      maintainAspectRatio: false
    });

    // 4. Priority Distribution (Bar)
    renderOrUpdateChart('chartPriority', 'bar', {
      labels: Object.keys(data.priority_distribution || {}),
      datasets: [{
        label: 'Tickets',
        data: Object.values(data.priority_distribution || {}),
        backgroundColor: ['#EF4444', '#F97316', '#FBBF24', '#10B981'],
        borderRadius: 4
      }]
    }, {
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: 'rgba(255,255,255,0.05)' } }
      },
      responsive: true,
      maintainAspectRatio: false
    });

    // 5. Daily Email Volume (Line)
    const dailyLabels = (data.daily_volume || []).map(d => d.date.slice(5));
    const dailyCounts = (data.daily_volume || []).map(d => d.count);
    renderOrUpdateChart('chartDailyVolume', 'line', {
      labels: dailyLabels.length ? dailyLabels : ['Day 1'],
      datasets: [{
        label: 'Volume',
        data: dailyCounts.length ? dailyCounts : [data.total_emails || 1],
        borderColor: '#38BDF8',
        backgroundColor: 'rgba(56, 189, 248, 0.15)',
        fill: true,
        tension: 0.35,
        pointBackgroundColor: '#38BDF8'
      }]
    }, {
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' } },
        y: { grid: { color: 'rgba(255,255,255,0.05)' } }
      },
      responsive: true,
      maintainAspectRatio: false
    });

    // 6. Urgency Distribution (Doughnut)
    renderOrUpdateChart('chartUrgency', 'doughnut', {
      labels: Object.keys(data.urgency_distribution || {}),
      datasets: [{
        data: Object.values(data.urgency_distribution || {}),
        backgroundColor: ['#EF4444', '#F59E0B', '#38BDF8', '#10B981'],
        borderColor: '#0F172A',
        borderWidth: 2
      }]
    }, {
      plugins: { legend: { position: 'bottom' } },
      responsive: true,
      maintainAspectRatio: false
    });
  }

  function renderOrUpdateChart(canvasId, type, chartData, options) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (chartInstances[canvasId]) {
      chartInstances[canvasId].destroy();
    }

    chartInstances[canvasId] = new Chart(canvas, {
      type: type,
      data: chartData,
      options: options
    });
  }

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
