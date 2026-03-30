// Performance audit utilities
export const auditListingCardPerformance = () => {
  const elements = document.querySelectorAll('[data-testid="listing-card"]');
  const issues: { type: string; element: string; issue: string; fix: string }[] = [];
  
  elements.forEach((card, index) => {
    const rect = card.getBoundingClientRect();
    const computedStyle = getComputedStyle(card);
    
    // Check for layout shifts
    if (rect.width === 0 || rect.height === 0) {
      issues.push({
        type: 'layout_shift',
        element: `ListingCard ${index}`,
        issue: 'Zero dimensions detected',
        fix: 'Add explicit width/height or aspect-ratio'
      });
    }
    
    // Check for CLS triggers
    if (computedStyle.position === 'static' && rect.height > 200) {
      issues.push({
        type: 'cls_risk',
        element: `ListingCard ${index}`,
        issue: 'Large static element may cause layout shift',
        fix: 'Add contain: layout or use position: relative'
      });
    }
  });
  
  return issues;
};

export const optimizeListingCards = () => {
  return {
    fixes: [
      'Add aspect-ratio to prevent layout shifts',
      'Use contain: layout for large elements',
      'Implement skeleton loading states',
      'Optimize image loading with lazy loading',
      'Add explicit dimensions to media elements'
    ]
  };
};
