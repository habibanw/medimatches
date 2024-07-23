 describe("Delete", () => {
    beforeEach(() => {
      cy.visit("/logout")
      cy.visit("/login")
    })
    it("Should delete the patient account", () => {
        cy.fixture("patient").then((user) => {

            cy.get("#id_email").type(user.username)
            cy.get("#id_password").type(user.password, { log: false })
            cy.get("#id_submit").click()
            cy.get('.messages').contains("Welcome")
            cy.visit("/delete_account")
            cy.get("#id_submit").click()

            cy.get('.messages').contains("Account deleted successfully")
        })
        cy.visit("/admin")
        cy.fixture("admin").then((admin) => {
            cy.get("#id_username").type(admin.admin_email)
            cy.get("#id_password").type(admin.admin_password, { log: false })
            cy.get('input[type="submit"]').click()

            cy.contains("Users").click()

            cy.contains('patient@test.com').click()
            cy.get('#id_is_active').check()
            cy.contains('Save').click()

            cy.visit('/logout')
        })
    })
    it("Should delete the provider account", () => {
        cy.fixture("provider").then((user) => {
            cy.get("#id_email").type(user.username)
            cy.get("#id_password").type(user.password, { log: false })
            cy.get("#id_submit").click()
  
            cy.get('.messages').contains("Welcome TAMMY")

            cy.visit("/delete_account")
            cy.get("#id_submit").click()

            cy.get('.messages').contains("Account deleted successfully")
        })
        cy.visit("/admin")
        cy.fixture("admin").then((admin) => {
            cy.get("#id_username").type(admin.admin_email)
            cy.get("#id_password").type(admin.admin_password, { log: false })
            cy.get('input[type="submit"]').click()

            cy.contains("Users").click()

            cy.contains('provider@test.com').click()
            cy.get('#id_is_active').check()
            cy.contains('Save').click()

            cy.visit('/logout')
        })  
    })
}) 