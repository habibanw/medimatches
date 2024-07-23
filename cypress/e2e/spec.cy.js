describe('Checks homepage loads', () => {
  it("visits the homepage", () => {
    cy.visit("/") // Arrange
    cy.get("h1.text-5xl").contains("Welcome to MediMatch") // Assert
  })
})