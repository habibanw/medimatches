describe("Login", () => {
    beforeEach(() => {
      cy.visit("/logout")
      cy.visit("/login")
    })
    it("Should try to log in with patient user", () => {
      cy.fixture("patient").then((user) => {
          cy.get("#id_email").type(user.username)
          cy.get("#id_password").type(user.password, { log: false })
          cy.get("#id_submit").click()

          cy.get('.messages').contains("Welcome")
      })  
    })
    it("Should try to log in with provider user", () => {
        cy.fixture("provider").then((user) => {
            cy.get("#id_email").type(user.username)
            cy.get("#id_password").type(user.password, { log: false })
            cy.get("#id_submit").click()
  
            cy.get('.messages').contains("Welcome TAMMY")
        })  
    })
    it("Should try to log in with unregistered user", () => {
        cy.fixture("unregistered").then((user) => {
            cy.get("#id_email").type(user.username)
            cy.get("#id_password").type(user.password, { log: false })
            cy.get("#id_submit").click()
  
            cy.get('.error').contains("Incorrect email or password")
        })  
      })
})