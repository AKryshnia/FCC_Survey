document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.tooltip-field').forEach(function(field) {
        field.addEventListener('focus', function() {
            var tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.style.position = 'absolute';
            tooltip.style.backgroundColor = '#333';
            tooltip.style.color = '#fff';
            tooltip.style.padding = '5px';
            tooltip.style.borderRadius = '5px';
            tooltip.style.fontSize = '12px';
            tooltip.style.zIndex = '1000';
            tooltip.style.marginTop = '5px';

            var options = field.querySelectorAll('option');
            var optionsText = Array.from(options).map(function(option) {
                return option.textContent;
            }).join(', ');

            tooltip.textContent = optionsText;
            field.parentElement.appendChild(tooltip);
        });

        field.addEventListener('blur', function() {
            var tooltip = field.parentElement.querySelector('.tooltip');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });
});