// n8n Code Node: Pipeline Health Check
// Runs daily at 7pm AWST — checks 7-day rolling metrics
// Auto-pauses Instantly campaigns if thresholds exceeded
//
// Input: Supabase query results from email_audit_log (last 7 days)
// Output: health report object + pause/continue decision

function calculateHealthMetrics(auditLogs) {
  const now = new Date();
  const sevenDaysAgo = new Date(now - 7 * 24 * 60 * 60 * 1000);

  // Filter to last 7 days
  const recent = auditLogs.filter(log =>
    new Date(log.sent_at) >= sevenDaysAgo
  );

  const total = recent.length;
  if (total === 0) {
    return {
      total_sent: 0,
      bounce_rate: 0,
      spam_rate: 0,
      reply_rate: 0,
      unsubscribe_rate: 0,
      status: 'no_data',
      action: 'continue',
      alerts: [],
    };
  }

  const bounced = recent.filter(l => l.status === 'bounced').length;
  const spam = recent.filter(l => l.status === 'spam_complaint').length;
  const replied = recent.filter(l => l.status === 'replied').length;
  const unsubscribed = recent.filter(l => l.status === 'unsubscribed').length;

  const bounceRate = (bounced / total) * 100;
  const spamRate = (spam / total) * 100;
  const replyRate = (replied / total) * 100;
  const unsubRate = (unsubscribed / total) * 100;

  const alerts = [];
  let action = 'continue';

  // Bounce rate thresholds
  if (bounceRate > 3) {
    alerts.push(`CRITICAL: Bounce rate ${bounceRate.toFixed(1)}% exceeds 3% — AUTO-PAUSING`);
    action = 'pause';
  } else if (bounceRate > 2) {
    alerts.push(`WARNING: Bounce rate ${bounceRate.toFixed(1)}% exceeds 2%`);
  }

  // Spam complaint thresholds
  if (spamRate > 0.3) {
    alerts.push(`CRITICAL: Spam rate ${spamRate.toFixed(2)}% exceeds 0.3% — AUTO-PAUSING`);
    action = 'pause';
  } else if (spamRate > 0.1) {
    alerts.push(`WARNING: Spam rate ${spamRate.toFixed(2)}% exceeds 0.1%`);
  }

  // Reply rate (too low = content issue)
  if (replyRate < 0.5 && total >= 50) {
    alerts.push(`WARNING: Reply rate ${replyRate.toFixed(1)}% is below 0.5% — review email content`);
  }

  // Unsubscribe rate
  if (unsubRate > 5) {
    alerts.push(`CRITICAL: Unsubscribe rate ${unsubRate.toFixed(1)}% exceeds 5% — AUTO-PAUSING`);
    action = 'pause';
  } else if (unsubRate > 3) {
    alerts.push(`WARNING: Unsubscribe rate ${unsubRate.toFixed(1)}% exceeds 3%`);
  }

  return {
    total_sent: total,
    bounced,
    spam_complaints: spam,
    replied,
    unsubscribed,
    bounce_rate: bounceRate.toFixed(2),
    spam_rate: spamRate.toFixed(3),
    reply_rate: replyRate.toFixed(2),
    unsubscribe_rate: unsubRate.toFixed(2),
    status: action === 'pause' ? 'unhealthy' : alerts.length > 0 ? 'warning' : 'healthy',
    action,
    alerts,
    checked_at: now.toISOString(),
  };
}

// A/B variant performance breakdown
function getVariantPerformance(auditLogs, leads) {
  const variants = {};

  for (const lead of leads) {
    if (!lead.email_variant) continue;
    if (!variants[lead.email_variant]) {
      variants[lead.email_variant] = { sent: 0, replied: 0, bounced: 0 };
    }
    variants[lead.email_variant].sent++;
    if (lead.responded_at) variants[lead.email_variant].replied++;
  }

  // Calculate response rates
  const performance = {};
  for (const [variant, stats] of Object.entries(variants)) {
    performance[variant] = {
      ...stats,
      reply_rate: stats.sent > 0 ? ((stats.replied / stats.sent) * 100).toFixed(1) + '%' : 'N/A',
    };
  }

  return performance;
}

// n8n Code node entry point
const auditLogs = $input.all().map(item => item.json);
const health = calculateHealthMetrics(auditLogs);

return [{ json: health }];
