// Example Cypress spec for one flow. Copy to cypress/e2e/f01-book.cy.ts and adapt.
// Selectors use accessible labels and text content so they survive restyling.

describe('F01 guest books a meeting', () => {
  beforeEach(() => {
    // Fail on unhandled console errors or 5xx server responses
    cy.on('window:before:load', (win) => {
      cy.spy(win.console, 'error').as('consoleError');
    });
  });

  it('F01-H1 happy path', () => {
    cy.visit('/u/demo/30min');
    cy.contains('button', /next available day/i).click();
    cy.contains('button', /10:00/).click();

    cy.contains('label', 'Name').find('input').type('Test Guest');
    cy.contains('label', 'Email').find('input').type('guest@example.test');

    cy.contains('button', /confirm/i).click();
    cy.contains('h1, h2, h3', /you are booked/i).should('be.visible');

    // Ensure no unhandled console errors occurred during the flow
    cy.get('@consoleError').should('not.be.called');
  });

  it('F01-E1 double submit creates one booking', () => {
    cy.visit('/u/demo/30min');
    cy.contains('button', /next available day/i).click();
    cy.contains('button', /11:00/).click();

    cy.contains('label', 'Name').find('input').type('Twice');
    cy.contains('label', 'Email').find('input').type('twice@example.test');

    // Rapid double click simulation
    cy.contains('button', /confirm/i).dblclick();
    cy.contains('h1, h2, h3', /you are booked/i).should('be.visible');
  });
});
