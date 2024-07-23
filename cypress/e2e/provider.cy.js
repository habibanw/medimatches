describe('Visit the provider list', () => {
    it("visits the privider list", () => {
      cy.visit("/providers") // Arrange
      cy.get("ul.listing").find("li").should('have.length', 50)
    })
    it("Should raise a 404 for an invalid provider", () => {
      cy.request({url: '/providers/1234567891010101010', failOnStatusCode: false}).its('status').should('equal', 404)
    }) 
})