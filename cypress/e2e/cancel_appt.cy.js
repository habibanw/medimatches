describe("Cancel Appointment", () => {
    beforeEach(() => {
        cy.visit("/logout")
    })
    it("Patient cancels scheduled appt", () => {

        // Log in as a patient
        cy.visit('/login')
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
                cy.visit(url + '/schedule_appt')
            });

            // Schedule an appointment
            // Get the current date and time
            const now = new Date();
            now.setDate(now.getDate() + 8); // Add a day to the current date
            const currentDate = now.toISOString().split('T')[0]; // Format as YYYY-MM-DD
            const hrPad = now.getHours().toString().padStart(2, '0');
            const minPad = now.getMinutes().toString().padStart(2, '0');
            const currentTime = hrPad + ':' + minPad; // Format as HH:mm
            cy.get("#id_appointment_date").type(currentDate)
            cy.get("#id_appointment_time").type(currentTime)

            // Submit the form
            cy.get("#id_submit").click()

            // Assert that appointment was successfully requested
            cy.get('.messages').contains('Appointment requested successfully');

            // Go to the appointments page
            cy.visit('/profile/appointments')
            cy.get('h1').contains("Appointment List")
            cy.get('#appointment').find("li").eq(0).click() // Select the first appointment
            cy.get('#cancel-link').click()

            // Assert that appointment was successfully cancelled
            cy.visit('/profile/appointments')
            cy.get('h1').contains("Appointment List")
            cy.get('#appointment').find("li").eq(0).get('#canceled-bool').contains('Canceled')

        })
          
    })
    it("Check the message in the provider's inbox for cancel update", () => {

        cy.visit('/login')
        cy.fixture("provider").then((provider) => {
            cy.get("#id_email").type(provider.username)
            cy.get("#id_password").type(provider.password, { log: false })
            cy.get("#id_submit").click()

            // Go to the inbox
            cy.visit('/profile/messages')
            cy.get('h1').contains("My Messages")
            cy.get('#messages #container').find("li").first().click()
            cy.get('#messages #container').find("li").first().find("div.toggle-content div.subject").should('contain', 'Appointment Cancelation')
        }) 
    })
    it("Provider cancels scheduled approved appt", () => {

        // Log in as a patient
        cy.visit('/login')
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
                cy.visit(url + '/schedule_appt')
            });

            // Schedule an appointment
            // Get the current date and time
            const now = new Date();
            now.setDate(now.getDate() + 8); // Add a day to the current date -> should be able to schedule an appointment since it has already been cancelled
            const currentDate = now.toISOString().split('T')[0]; // Format as YYYY-MM-DD
            const hrPad = now.getHours().toString().padStart(2, '0');
            const minPad = now.getMinutes().toString().padStart(2, '0');
            const currentTime = hrPad + ':' + minPad; // Format as HH:mm
            cy.get("#id_appointment_date").type(currentDate)
            cy.get("#id_appointment_time").type(currentTime)

            // Submit the form
            cy.get("#id_submit").click()

            // Assert that appointment was successfully requested
            cy.get('.messages').contains('Appointment requested successfully');

        })

        cy.visit("/logout")

        // Log in as a provider
        cy.visit('/login')
        cy.fixture("provider").then((provider) => {
            cy.get("#id_email").type(provider.username)
            cy.get("#id_password").type(provider.password, { log: false })
            cy.get("#id_submit").click()

            // Go to the appointments page
            cy.visit('/profile/appointments')
            cy.get('h1').contains("Appointment List")
            cy.get('#appointment').find("li").first().click()
            cy.get('#approve-button').click()

            // Assert that appointment was successfully approved
            cy.get('#appointment-status').contains('Approved');

            // Go to the appointments page
            cy.visit('/profile/appointments')
            cy.get('h1').contains("Appointment List")
            cy.get('#appointment').find("li").eq(0).click() // Select the first appointment
            cy.get('#cancel-link').click()

            // Assert that appointment was successfully cancelled
            cy.visit('/profile/appointments')
            cy.get('h1').contains("Appointment List")
            cy.get('#appointment').find("li").eq(0).get('#canceled-bool').contains('Canceled')
        })
          
    })
    it("Check the message in the patient's inbox for cancel update", () => {

        cy.visit('/login')
        cy.fixture("patient").then((patient) => {
            cy.get("#id_email").type(patient.username)
            cy.get("#id_password").type(patient.password, { log: false })
            cy.get("#id_submit").click()

            // Go to the inbox
            cy.visit('/profile/messages')
            cy.get('h1').contains("My Messages")
            cy.get('#messages #container').find("li").first().click()
            cy.get('#messages #container').find("li").first().find("div.toggle-content div.subject").should('contain', 'Appointment Cancelation')
        }) 
    })

})