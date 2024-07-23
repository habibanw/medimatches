describe("Send message", () => {
    beforeEach(() => {
      cy.visit("/logout")
    })
    it("Should redirect to the log in form when user is anonymous", () => {
        cy.visit('/providers')
        cy.get('ul.listing').find('li').first().find('a').first().click()
        cy.url().then(url => {
            cy.visit(url + '/send_message')
        });

        cy.url().should("include", "login")
        cy.title().should("include", "Login Page")
        cy.get('.error').contains("You must log in to send a message.")
    })
    it("Should not allow a logged in user to message an un-registered provider", () => {
        cy.fixture("patient").then((patient) => {
            cy.get("#id_email").type(patient.username)
            cy.get("#id_password").type(patient.password, { log: false })
            cy.get("#id_submit").click()

            cy.visit('/providers')
            cy.get('ul.listing').find('li').first().find('a').first().click()
            cy.url().then(url => {
                cy.visit(url + '/send_message')
            });
            cy.get('.error').contains("This provider has not claimed their profile and MediMatch and cannot receive messages.")
        })
    })
    it("Should not allow a logged in user to message a non-existent provider", () => {
        cy.fixture("patient").then((patient) => {
            cy.get("#id_email").type(patient.username)
            cy.get("#id_password").type(patient.password, { log: false })
            cy.get("#id_submit").click()

            cy.visit('/providers/1234567891010101010/send_message', {failOnStatusCode: false})
            cy.get('h2').should("contain", "404 Page")
            cy.get('div.error').should("contain", "There is no provider record associated with this profile.")
        })
    })
})