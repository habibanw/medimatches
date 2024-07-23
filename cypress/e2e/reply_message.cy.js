describe("Reply message", () => {
    beforeEach(() => {
      cy.visit("/logout")
    })
    it("check if user gets the replied message", () => {
        cy.fixture("patient").then((patient) => {
            cy.get("#id_email").type(patient.username)
            cy.get("#id_password").type(patient.password, { log: false })
            cy.get("#id_submit").click()

            // Go to providers page
            cy.visit('/providers')
            cy.get("#id_name_query").type("TAMMY JONES", { log: false })
            cy.get("#id_state").select("WV")
            cy.get("#id_search").click()
            cy.get('ul.listing').find('li').first().find('a').first().click()
            cy.url().then(url => {
                cy.visit(url + '/send_message')
            });

            // Send a message
            cy.get("#id_subject").type("Test Subject")
            cy.get("#id_content").type("I am testing the message feature.")
            cy.get("#id_submit").click()

            // Assert that message was successfully sent
            cy.get('.messages').contains('Message sent successfully');

            // Log out
            cy.visit('/logout')

            // Log in as a provider
            cy.visit('/login')
            cy.fixture("provider").then((user) => {
                cy.get("#id_email").type(user.username)
                cy.get("#id_password").type(user.password, { log: false })
                cy.get("#id_submit").click()
            })

            // Go to the inbox
            cy.visit('/profile/messages')
            cy.get('h1').contains("My Messages")
            cy.get('#messages #container').find("li").first().click()
            cy.get('#messages #container').find("li").first().find("div.toggle-content div.subject").should('contain', 'Test Subject')
            cy.get("#messages #container").find("li").first().click()
            
            // Reply to the message
            cy.get("#messages #container").find("li").first().find("div.toggle-content div#reply_message a").click()

            cy.get("#id_content").type("I am testing the reply feature.")

            // Submit the form
            cy.get("#id_submit").click()

            // Assert that message was successfully replied
            cy.get('.messages').contains('Reply sent successfully');

            // Log out
            cy.visit('/logout')

            // Log in as a patient
            cy.visit('/login')
            cy.fixture("patient").then((patient) => {
                cy.get("#id_email").type(patient.username)
                cy.get("#id_password").type(patient.password, { log: false })
                cy.get("#id_submit").click()
            })

            // Go to the inbox
            cy.visit('/profile/messages')
            cy.get('h1').contains("My Messages")
            cy.get('#messages #container').find("li").first().click()
            cy.get('#messages #container').find("li").first().find("div.toggle-content div.subject").should('contain', 'Re: Test Subject')
            cy.get("#messages #container").find("li").first().click()
            cy.get("#messages #container").find("li").first().find("div.toggle-content p").should('contain', 'I am testing the reply feature.')
        })
    })
})