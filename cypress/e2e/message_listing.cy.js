describe("Messages", () => {
    beforeEach(() => {
      cy.visit("/logout")
    })
    it("Should redirect a logged out user to the login form", () => {
        cy.visit('/profile/messages')
        cy.url().should("include", "login")
        cy.title().should("include", "Login Page")
    })
    it("Should show an empty message list", () => {
        cy.fixture("patient2").then((patient) => {

            cy.get("#id_email").type(patient.username)
            cy.get("#id_password").type(patient.password, { log: false })
            cy.get("#id_submit").click()

            cy.visit("/profile/messages")
            cy.get('h1').contains("My Messages")
            cy.get('p').contains("You have no messages")

        })
    })
    it("Should show a message list", () => {
        cy.fixture("provider").then((provider) => {

            cy.get("#id_email").type(provider.username)
            cy.get("#id_password").type(provider.password)
            cy.get("#id_submit").click()

            cy.visit("/profile/messages")
            cy.get('h1').contains("My Messages")
            cy.get('#messages #container').find("li").first().click()
            cy.get('#messages #container').find("li").first().find("div.toggle-content div.subject").should('contain', 'Appointment Request')
        })
    })
    it("Should show a delete link on message list", () => {
        cy.fixture("provider").then((provider) => {

            cy.get("#id_email").type(provider.username)
            cy.get("#id_password").type(provider.password)
            cy.get("#id_submit").click()

            cy.visit("/profile/messages")
            cy.get('h1').contains("My Messages")
            cy.get('#messages #container').find("li").first().click()
            cy.get('#messages #container').find("li").first().find("div.toggle-content a").should('contain', 'Delete this message')
        })
    })
    it("Should raise a 404 for an invalid message", () => {
        cy.fixture("provider").then((provider) => {

            cy.get("#id_email").type(provider.username)
            cy.get("#id_password").type(provider.password)
            cy.get("#id_submit").click()

            cy.visit("/profile/messages")
            
            cy.visit("/profile/messages/1234567891010101010/delete")
            cy.get("h2").should('contain', "404 Page")
        })
      }) 
})